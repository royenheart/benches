#!/usr/bin/env python3
"""Generate the teaching figures for the orchestration chapter.

Orchestration-layer diagram (Okabe-Ito colorblind-safe palette, Noto Sans CJK SC,
300 DPI PNG + vector PDF):
  fig3_workflow_landscape  — the unified-workflow-YAML question, answered visually

Run:  python gen_figures.py        (from images/ or anywhere; outputs land here)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent

plt.rcParams.update(
    {
        "font.family": ["Noto Sans CJK SC", "DejaVu Sans"],
        "font.size": 9,
        "axes.edgecolor": "#444444",
        "figure.facecolor": "white",
    }
)

# Okabe-Ito
BLUE, ORANGE, GREEN, PURPLE, SKY, VERM, YELLOW, GREY = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#D55E00",
    "#F0E442",
    "#7F7F7F",
)


def box(ax, x, y, w, h, text, fc="#FFFFFF", ec=GREY, fs=9, lw=1.2, weight="normal", rounding=0.06):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.008,rounding_size={rounding}",
            fc=fc, ec=ec, lw=lw, zorder=2,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight=weight, zorder=3)


def arrow(ax, x1, y1, x2, y2, text="", color=GREY, style="-|>", fs=8, ls="-", text_dy=0.02, text_dx=0.0, lw=1.4):
    ax.add_patch(
        FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=13, color=color, lw=lw, ls=ls, zorder=1)
    )
    if text:
        ax.text((x1 + x2) / 2 + text_dx, (y1 + y2) / 2 + text_dy, text, ha="center", va="bottom", fontsize=fs, color=color)


def new_ax(w=10, h=6.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    for ext in ("png", "pdf"):
        path = HERE / f"{name}.{ext}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(f"wrote {path}")
    plt.close(fig)


# ---------------------------------------------------------------- fig 3
def fig3():
    fig, ax = new_ax(10, 6.4)
    ax.text(0.02, 0.965, "“统一工作流 YAML”格局：共同结构已收敛，执行语义仍各自为政", fontsize=13, weight="bold")
    ax.text(0.02, 0.925, "回答：能否写一份 YAML 交给各种框架解析？—— 今天不能整体做到，但“共同分母”已经足够小，可以自己做一层", fontsize=8.6, color=GREY)

    # common denominator chips (two rows to stay inside the canvas)
    ax.text(0.02, 0.855, "所有格式的共同结构（Agent 编排真正需要的全部）：", fontsize=9.5, weight="bold")
    chips = [
        ["triggers（cron/webhook/事件）", "steps + needs（DAG）", "typed output（JSON Schema）"],
        ["retries / timeout", "approval 审批门", "幂等 + 运行账本"],
    ]
    for row, chip_row in enumerate(chips):
        x = 0.02
        y = 0.795 - row * 0.055
        for c in chip_row:
            w = 0.026 + len(c) * 0.0080
            box(ax, x, y, w, 0.042, c, fc="#EAF3FA", ec=BLUE, fs=8, rounding=0.012)
            x += w + 0.014
    ax.text(0.02, 0.70, "演示：scripts/workflow_dsl_demo.py 用一份 JSON(=YAML 子集) 文档真实执行，并机械翻译成 Kestra / OpenFlow / Argo 三种语法",
            fontsize=8, color=BLUE)

    # portability spectrum
    ax.text(0.02, 0.645, "可移植性光谱（同一份定义，能否换个引擎继续跑？）", fontsize=9.5, weight="bold")
    segs = [
        ("n8n / Dify DSL", "引擎私有", 0.15, "#F4D7CE"),
        ("Kestra / OpenFlow / Argo", "语法开放、语义私有", 0.22, "#FCE8C8"),
        ("MS Agent FW YAML\nOracle Agent Spec", "agent 定义层\n开始收敛（2026）", 0.25, "#FDF6D8"),
        ("BPMN 2.0 XML", "唯一多引擎通用\n（不 agent-native）", 0.17, "#DFF0E4"),
        ("Open Workflow DSL", "CNCF；多实现、小众", 0.15, "#DCEEF7"),
    ]
    x = 0.02
    for label, sub, w, fc in segs:
        ax.add_patch(FancyBboxPatch((x, 0.525), w, 0.095, boxstyle="round,pad=0.006,rounding_size=0.01", fc=fc, ec=GREY, lw=0.8))
        ax.text(x + w / 2, 0.588, label, ha="center", va="center", fontsize=7.4, weight="bold")
        ax.text(x + w / 2, 0.551, sub, ha="center", va="center", fontsize=7.0, color="#555555")
        x += w + 0.004
    arrow(ax, 0.02, 0.50, 0.97, 0.50, "", color=GREY)
    ax.text(0.02, 0.472, "私有", fontsize=8, color=GREY)
    ax.text(0.93, 0.472, "通用", fontsize=8, color=GREY)

    # temporal contrast
    box(ax, 0.03, 0.30, 0.45, 0.15,
        "Temporal：另一条路 —— workflow-as-code（无官方 YAML）\n\n"
        "· 持久执行：代码从事件历史重放，崩溃自动续跑\n"
        "· 审批 = signal，状态 = query，重试 = activity 策略\n"
        "· MIT；PostgreSQL + 2GB 内存即可自托管；start-dev 本地即起\n"
        "· 2026 已 GA：OpenAI Agents SDK 集成、LangGraph 插件、ADK",
        fc="#F7F7F7", ec=VERM, fs=8, lw=1.4)
    box(ax, 0.52, 0.30, 0.45, 0.15,
        "实践结论（对应 cloud-agent 的 §11 决策）\n\n"
        "· 短 DAG + 审批：Postgres + 租约的小执行器就够（本 demo）\n"
        "· 小时-天级长任务 / 多 worker：再引入 Temporal\n"
        "· 自研 workflows.yml 只依赖“共同分母”，可翻译到 Kestra 等\n"
        "· 不要把 LLM 写进触发判断 —— 触发器保持确定性",
        fc="#F7F7F7", ec=GREEN, fs=8, lw=1.4)

    ax.text(0.02, 0.24, "参考：CNCF Open Workflow DSL（原 Serverless Workflow）· Kestra · Windmill OpenFlow · Argo · Temporal docs · Oracle Agent Spec（2025-10）",
            fontsize=7.2, color=GREY)
    save(fig, "fig3_workflow_landscape")


if __name__ == "__main__":
    fig3()
