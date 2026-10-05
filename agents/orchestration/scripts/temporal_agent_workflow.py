"""Temporal agent workflow with human approval — reference example.

This is the code-first contrast to workflow_dsl_demo.py: Temporal has NO YAML workflow layer; orchestration logic lives in deterministic workflow code and the runtime replays it from an append-only event history ("durable execution"). Approvals are *signals*, status is a *query*.

Prerequisites (not part of the stdlib toy mode):
    pip install temporalio
    temporal server start-dev        # local dev server (Temporal CLI)

Then in two terminals:
    python temporal_agent_workflow.py worker      # long-running worker
    python temporal_agent_workflow.py start       # starts a workflow run

Verified facts behind this example (see chapter README):
  * Server license MIT; persistence = PostgreSQL/MySQL/Cassandra; a 2 GB box with Postgres is a documented minimal self-host.
  * `temporal server start-dev` embeds everything for local dev.
  * Agent integrations GA in 2026: OpenAI Agents SDK (2026-03), LangGraph plugin (2026-07), Google ADK; community MCP servers can drive workflows.
  * Community YAML layers exist (Zigflow, Code-Exchange "Temporal DSL") but none are official — workflows-as-code is the durable-execution sweet spot.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import timedelta

try:
    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.worker import Worker
except ImportError:  # pragma: no cover - teaching script
    sys.exit(
        "temporalio is not installed.\n"
        "  pip install temporalio\n"
        "  temporal server start-dev   # from https://docs.temporal.io/cli\n"
        "Then re-run: python temporal_agent_workflow.py [worker|start]"
    )


@dataclass
class Approval:
    approved: bool
    approver: str


@activity.defn
async def call_llm(prompt: str) -> str:
    """Stand-in for the real LLM/agent call. Activities (not workflows) are
    where side effects and non-determinism live — they get automatic retries."""
    return f"[toy-llm] draft answer for: {prompt[:40]}"


@workflow.defn
class AgentApprovalWorkflow:
    """Agent step -> wait for a human approval signal -> finalize.

    Crash-safe by construction: if the worker dies while waiting, Temporal
    re-schedules the workflow and it resumes at wait_condition with the
    signal's event already journaled.
    """

    def __init__(self) -> None:
        self.approval: Approval | None = None
        self.draft: str = ""

    @workflow.run
    async def run(self, prompt: str) -> str:
        self.draft = await workflow.execute_activity(
            call_llm, prompt, schedule_to_close_timeout=timedelta(seconds=30)
        )
        # HITL: block (up to 24h) until a signal arrives. No polling, no state
        # machine to hand-roll — the event history IS the state machine.
        await workflow.wait_condition(lambda: self.approval is not None, timeout=timedelta(hours=24))
        if not self.approval.approved:
            return f"REJECTED by {self.approval.approver}: {self.draft}"
        return f"PUBLISHED by {self.approval.approver}: {self.draft}"

    @workflow.signal
    async def submit_approval(self, approval: Approval) -> None:
        self.approval = approval

    @workflow.query
    def current_status(self) -> dict:
        return {"draft": self.draft, "approval": self.approval}


TASK_QUEUE = "agent-approval-demo"


async def run_worker():
    client = await Client.connect("localhost:7233")
    worker = Worker(client, task_queue=TASK_QUEUE, workflows=[AgentApprovalWorkflow], activities=[call_llm])
    await worker.run()


async def start_workflow():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        AgentApprovalWorkflow.run, "summarize yesterday's incidents", id=f"agent-run-1", task_queue=TASK_QUEUE
    )
    print(f"started {handle.id}; status={handle.query(AgentApprovalWorkflow.current_status)}")
    await asyncio.sleep(1)
    # Human decision arrives out-of-band as a signal:
    await handle.signal(AgentApprovalWorkflow.submit_approval, Approval(approved=True, approver="oncall-human"))
    result = await handle.result()
    print(f"result: {result}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("worker", "start"):
        sys.exit(__doc__)
    asyncio.run(run_worker() if sys.argv[1] == "worker" else start_workflow())
