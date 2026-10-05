"""Workflow-as-data demo: one portable document, a mini engine, engine ports.

Answers the question "can the orchestration layer have ONE unified format that different engines parse?" by showing:

  * The common structural denominator of workflow DSLs: triggers / steps / needs (DAG) / typed outputs / retries / timeouts / approval gates.
  * JSON is a subset of YAML — so a JSON document IS a YAML document, and the "unified YAML" discussion is really about the *schema*, not the syntax.
  * The same document mechanically re-rendered as Kestra YAML, Windmill OpenFlow and an Argo Workflow (teaching approximations, see --show-ports).
  * A mini DAG executor (stdlib only) that runs the document for real: topological order, template expansion (${{ steps.X.output }}), an approval gate (interactive, or --auto-approve), and an append-only run ledger persisted atomically (tmp file + os.replace) — the same pattern as MaintainAll's storages/*.json.

Two built-in documents:

  * "nightly-report" — the minimal teaching DAG (collect -> draft -> approve -> send).
  * "incident-response" — a realistic shape: SQL view -> provision a sandbox via the broker -> two agent prompts -> approval -> publish/teardown. Mirrors examples/incident-response/workflow.json, which is rendered by hand into Kestra / Windmill / Argo / GitHub Actions syntax in the same directory — open those files side by side to see "open syntax, private semantics" concretely.

Usage:
    python workflow_dsl_demo.py                                 # execute nightly-report
    python workflow_dsl_demo.py --workflow incident-response    # execute the realistic one
    python workflow_dsl_demo.py --file path/to/workflow.json    # execute your own document
    python workflow_dsl_demo.py --auto-approve                  # non-interactive run
    python workflow_dsl_demo.py --show-ports [--workflow W]     # print Kestra/OpenFlow/Argo renderings
    python workflow_dsl_demo.py --workdir /tmp/wfdemo
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import uuid
from pathlib import Path

# One document, engine-neutral. `needs` makes the DAG; `approval` is a
# first-class step type (the one primitive Temporal/Kestra/Windmill/Orca all
# converged on independently).
WORKFLOW_NIGHTLY = {
    "id": "nightly-report",
    "version": "0.1",
    "triggers": [{"type": "cron", "cron": "0 3 * * *"}],
    "steps": [
        {
            "id": "collect",
            "type": "agent",
            "agent": "researcher",
            "prompt": "Collect yesterday's ops incidents",
            "output": {"type": "object", "schema": {"incidents": "list[str]"}},
            "retries": 2,
        },
        {
            "id": "draft",
            "type": "agent",
            "agent": "writer",
            "needs": ["collect"],
            "prompt": "Write a summary of: ${{ steps.collect.output }}",
            "retries": 2,
        },
        {"id": "approve", "type": "approval", "needs": ["draft"], "approvers": ["oncall-human"]},
        {
            "id": "send",
            "type": "agent",
            "agent": "publisher",
            "needs": ["approve"],
            "prompt": "Publish the approved report",
        },
    ],
}

# Realistic shape (SQL -> sandbox -> agents -> approval -> publish).
# The step types (sql / provision / agent / approval / notify) are OUR engine's
# semantics — every other engine expresses them differently; see
# examples/incident-response/ for the same workflow in 4 foreign syntaxes.
WORKFLOW_INCIDENT = {
    "id": "incident-response",
    "version": "0.1",
    "triggers": [{"type": "cron", "cron": "0 8 * * *"}],
    "defaults": {"retries": {"max_attempts": 3, "backoff": "exponential", "interval": "30s"}},
    "steps": [
        {
            "id": "fetch-view",
            "type": "sql",
            "engine": "postgres",
            "statement": "SELECT * FROM v_daily_incidents WHERE day = '${{ trigger.date }}'",
            "output": {"type": "array", "items": {"type": "object"}},
        },
        {
            "id": "provision-env",
            "type": "provision",
            "needs": ["fetch-view"],
            "backend": {
                "image": "ops-agent-base:3",
                "tier": "container",
                "ttl_sec": 1800,
                "egress": {"pypi": True, "npm": False},
            },
            "output": {"type": "object", "schema": {"sandbox_id": "string", "endpoint": "string"}},
        },
        {
            "id": "agent-triage",
            "type": "agent",
            "needs": ["provision-env"],
            "agent": "triage-bot",
            "prompt": "事件初判严重级别（P0-P3）：${{ steps.fetch-view.output }}",
            "output": {"type": "object"},
        },
        {
            "id": "agent-draft",
            "type": "agent",
            "needs": ["agent-triage"],
            "agent": "writer-bot",
            "prompt": "为 P0/P1 起草处理建议：${{ steps.agent-triage.output }}",
            "output": {"type": "object"},
        },
        {
            "id": "approve-plan",
            "type": "approval",
            "needs": ["agent-draft"],
            "approvers": ["oncall-human"],
        },
        {
            "id": "publish",
            "type": "notify",
            "needs": ["approve-plan"],
            "channel": "ops-channel",
            "teardown": ["provision-env"],
        },
    ],
}

WORKFLOWS = {"nightly-report": WORKFLOW_NIGHTLY, "incident-response": WORKFLOW_INCIDENT}


# --- Mini engine ---------------------------------------------------------------


def topo_order(doc: dict) -> list[dict]:
    steps = {s["id"]: s for s in doc["steps"]}
    order: list[str] = []
    done: set[str] = set()

    def visit(sid: str):
        if sid in done:
            return
        for dep in steps[sid].get("needs", []):
            visit(dep)
        done.add(sid)
        order.append(sid)

    for s in doc["steps"]:
        visit(s["id"])
    return [steps[sid] for sid in order]


def render(template: str, outputs: dict[str, str]) -> str:
    out = template
    for sid, value in outputs.items():
        out = out.replace("${{ steps." + sid + ".output }}", value)
    return out


# Step handlers: the *semantics* of each step type live here — this is the
# "private" part every engine re-implements differently.
def run_sql(step: dict, ctx: dict) -> str:
    print(f"  → [sql/{step['engine']}] {step['statement']}")
    rows = [{"id": 101, "svc": "billing", "level": "P1"}, {"id": 102, "svc": "search", "level": "P3"}]
    print(f"  ← {len(rows)} rows (toy result)")
    return json.dumps(rows, ensure_ascii=False)


def run_provision(step: dict, ctx: dict) -> str:
    b = step["backend"]
    print(f"  → POST http://sandbox-broker:8080/sandboxes {{image: {b['image']}, tier: {b['tier']}, ttl: {b['ttl_sec']}s, egress: {b['egress']}}}")
    handle = {"sandbox_id": f"sbx-{uuid.uuid4().hex[:6]}", "endpoint": "http://10.0.0.23:4123", "tier": b["tier"]}
    print(f"  ← 201 {handle}   (到期自动暂停；broker 决定 tier 落到哪个 runner)")
    return json.dumps(handle)


def run_agent(step: dict, ctx: dict) -> str:
    return f"[{step['agent']}] done: {ctx['prompt'][:48]}"


def run_notify(step: dict, ctx: dict) -> str:
    print(f"  → publish to #{step['channel']} (toy)")
    for dep in step.get("teardown", []):
        handle = json.loads(ctx["outputs"][dep])
        print(f"  → DELETE http://sandbox-broker:8080/sandboxes/{handle['sandbox_id']}  (teardown)")
    return "published"


def append_ledger(workdir: Path, record: dict):
    """Atomic single-writer JSON persistence (MaintainAll storages pattern)."""
    runs = workdir / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    path = runs / f"{record['run_id']}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    os.replace(tmp, path)
    return path


def execute(doc: dict, workdir: Path, auto_approve: bool, verbose: bool) -> dict:
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    outputs: dict[str, str] = {}
    ledger = {"run_id": run_id, "workflow": doc["id"], "started_at": time.time(), "events": []}

    def log(event: str, **kv):
        ledger["events"].append({"t": round(time.time(), 3), "event": event, **kv})
        print(f"  [{event}] {kv}")

    handlers = {"sql": run_sql, "provision": run_provision, "agent": run_agent, "notify": run_notify}
    terminal = doc["steps"][-1]["id"]

    print(f"# executing workflow {doc['id']!r}  run={run_id}\n")
    for step in topo_order(doc):
        stype = step.get("type", "agent")
        if stype == "approval":
            log("approval_requested", step=step["id"], approvers=step.get("approvers", []))
            if auto_approve:
                decision = "approved"
            else:
                decision = input(f"  >> approve step {step['id']!r}? [y/n] ").strip().lower()
                decision = "approved" if decision in ("y", "yes") else "rejected"
            log("approval_resolved", step=step["id"], decision=decision)
            if decision != "approved":
                log("run_failed", reason=f"approval rejected at {step['id']}")
                break
            outputs[step["id"]] = "approved"
            continue
        prompt = render(step.get("prompt") or step.get("statement") or "", outputs)
        log("step_started", step=step["id"], type=stype)
        outputs[step["id"]] = handlers[stype](step, {"outputs": outputs, "prompt": prompt})
        log("step_completed", step=step["id"], output=outputs[step["id"]][:80])

    ledger["status"] = "completed" if terminal in outputs else "failed"
    ledger["finished_at"] = time.time()
    path = append_ledger(workdir, ledger)
    print(f"\n# run {ledger['status']}; ledger -> {path}")
    return ledger


# --- Ports: same document, other engines' syntax (teaching approximations) -------


def port_kestra(doc: dict) -> str:
    lines = [f"id: {doc['id']}", "namespace: demo", "tasks:"]
    for s in doc["steps"]:
        if s.get("type") == "approval":
            lines += [f"  - id: {s['id']}", "    type: io.kestra.plugin.core.flow.Pause"]
        elif s.get("type") == "sql":
            lines += [f"  - id: {s['id']}", "    type: io.kestra.plugin.jdbc.postgresql.Query", f"    sql: {s['statement']}"]
        else:
            lines += [f"  - id: {s['id']}", "    type: io.kestra.plugin.fs.http.Request", f"    # -> agent/sandbox endpoint for step {s['id']}"]
        deps = s.get("needs", [])
        if deps:
            lines.append(f"    dependsOn: [{', '.join(deps)}]")
    trig = doc["triggers"][0]
    lines += ["triggers:", "  - id: cron", "    type: io.kestra.plugin.core.trigger.Schedule", f"    cron: {trig['cron']}"]
    return "\n".join(lines)


def port_openflow(doc: dict) -> str:
    mods = []
    for s in doc["steps"]:
        if s.get("type") == "approval":
            mods.append(f"    - type: approval\n      id: {s['id']}\n      # suspends the flow until a human approves in the Windmill UI")
        elif s.get("type") == "sql":
            mods.append(f"    - type: rawscript\n      id: {s['id']}\n      # python script with a Windmill postgres resource; runs: {s.get('statement','')[:40]}")
        else:
            mods.append(f"    - type: rawscript\n      id: {s['id']}\n      # module calls agent/sandbox HTTP endpoint for step {s['id']}")
    summary = "summary: port of " + doc["id"] + " (OpenFlow schema, simplified)"
    return summary + "\nvalue:\n  modules:\n" + "\n".join(mods)


def port_argo(doc: dict) -> str:
    tasks = []
    for s in doc["steps"]:
        dep = s.get("needs", [])
        tasks.append(
            f"""  - name: {s['id']}
    template: {s.get('type', 'agent')}-step
    arguments:
      parameters: [{{name: step, value: {s['id']}}}]
    dependencies: [{', '.join(dep)}]"""
        )
    return "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nspec:\n  entrypoint: main\n  templates:\n  - name: main\n    dag:\n      tasks:\n" + "\n".join(tasks)


# --- Main -------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workflow", choices=sorted(WORKFLOWS), default="nightly-report")
    parser.add_argument("--file", type=Path, help="load a workflow JSON document instead of the built-in ones")
    parser.add_argument("--auto-approve", action="store_true", help="approve gates automatically (CI mode)")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--workdir", type=Path, default=Path(tempfile.gettempdir()) / "wfdemo")
    parser.add_argument("--show-ports", action="store_true", help="print Kestra/OpenFlow/Argo renderings and exit")
    args = parser.parse_args()

    doc = json.loads(args.file.read_text()) if args.file else WORKFLOWS[args.workflow]

    if args.show_ports:
        print("== Same document, three engine ports (teaching approximations) ==\n")
        print("--- Kestra (YAML, everything-is-YAML) ---\n" + port_kestra(doc))
        print("\n--- Windmill OpenFlow (flow.yaml) ---\n" + port_openflow(doc))
        print("\n--- Argo Workflows (Kubernetes CRD) ---\n" + port_argo(doc))
        print("\n# Note the common denominator: triggers / steps / needs(DAG) / approval / retries.")
        return

    args.workdir.mkdir(parents=True, exist_ok=True)
    execute(doc, args.workdir, args.auto_approve, args.verbose)


if __name__ == "__main__":
    main()
