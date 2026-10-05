#!/usr/bin/env python3
"""Generate the teaching figures for the orchestration chapter.

Protocol-layer diagrams (Okabe-Ito colorblind-safe palette, Noto Sans CJK SC,
300 DPI PNG + vector PDF):
  fig1_protocol_boundaries — who talks to whom, over what transport
  fig2_a2a_wire            — A2A v1 discovery / JSON-RPC / SSE on one timeline


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


# ---------------------------------------------------------------- fig 1
def fig1():
    fig, ax = new_ax(10, 6.4)
    ax.text(0.02, 0.965, "Agent 互操作协议地图：谁和谁说话、走什么传输", fontsize=13, weight="bold")
    ax.text(0.02, 0.925, "四种协议覆盖四个边界；全部以 JSON-RPC 2.0 语义为核心，只是载体不同", fontsize=9, color=GREY)

    # central agent
    box(ax, 0.38, 0.44, 0.24, 0.13, "Agent 运行时\n(你的编排对象)", fc="#EAF3FA", ec=BLUE, fs=10, weight="bold")

    # four peers
    box(ax, 0.04, 0.70, 0.24, 0.14, "工具 / 数据服务\nMCP Server", fc="#F3F7ED", ec=GREEN, fs=10, weight="bold")
    box(ax, 0.72, 0.70, 0.24, 0.14, "另一个 Agent\n(远程、异构)", fc="#FDF4E7", ec=ORANGE, fs=10, weight="bold")
    box(ax, 0.04, 0.14, 0.24, 0.14, "用户界面\n(Web / App)", fc="#F5EEF3", ec=PURPLE, fs=10, weight="bold")
    box(ax, 0.72, 0.14, 0.24, 0.14, "代码编辑器\n(Zed / JetBrains)", fc="#EEF6FB", ec=SKY, fs=10, weight="bold")

    # MCP: agent -> tool
    arrow(ax, 0.38, 0.56, 0.20, 0.70, "调用工具 / 读写资源", color=GREEN, text_dy=0.01)
    ax.text(0.155, 0.585, "stdio（子进程）\n或 Streamable HTTP\n单端点 POST + 请求级 SSE", fontsize=7.5, color=GREEN, ha="center")

    # A2A: agent <-> agent
    arrow(ax, 0.62, 0.575, 0.74, 0.70, "派发任务 / 取回结果", color=ORANGE, text_dy=-0.045)
    ax.text(0.845, 0.565, "HTTP 上三种绑定任选：\nJSON-RPC 2.0（+SSE 流）\ngRPC（HTTP/2 流）\nHTTP+JSON REST", fontsize=7.5, color=ORANGE, ha="center")

    # AG-UI: UI <-> agent
    arrow(ax, 0.20, 0.28, 0.38, 0.46, "事件流（运行/工具/HITL）", color=PURPLE, text_dy=-0.04, text_dx=0.05)
    ax.text(0.16, 0.375, "HTTP POST + SSE\n31 种事件（v1.0）", fontsize=7.5, color=PURPLE, ha="center")

    # ACP: editor <-> agent
    arrow(ax, 0.76, 0.28, 0.62, 0.455, "编辑器驱动编码 agent", color=SKY, text_dy=-0.04, text_dx=-0.02)
    ax.text(0.845, 0.375, "JSON-RPC 2.0 over stdio\n客户端拉起 agent 子进程\n双向：fs/terminal 由编辑器提供", fontsize=7.5, color=SKY, ha="center")

    # bottom strip
    box(ax, 0.04, 0.015, 0.92, 0.075,
        "共同底座：JSON-RPC 2.0 语义（方法 + id + result/error）   ·   发现差异：A2A 用 Agent Card，ACP/MCP 用 initialize 握手，AG-UI 直连端点",
        fc="#F7F7F7", ec=GREY, fs=8.5)
    save(fig, "fig1_protocol_boundaries")


# ---------------------------------------------------------------- fig 2
def fig2():
    fig, ax = new_ax(10, 6.6)
    ax.text(0.02, 0.965, "A2A v1 线级交互：一次调用在传输层长什么样", fontsize=13, weight="bold")
    ax.text(0.02, 0.925, "对应 demo：scripts/a2a_wire_demo.py --verbose 可以看到同样的字节", fontsize=9, color=GREY)

    # lifelines
    cx, sx = 0.22, 0.78
    box(ax, cx - 0.085, 0.845, 0.17, 0.05, "Client", fc="#EAF3FA", ec=BLUE, fs=10, weight="bold")
    box(ax, sx - 0.085, 0.845, 0.17, 0.05, "Agent Server", fc="#FDF4E7", ec=ORANGE, fs=10, weight="bold")
    for x in (cx, sx):
        ax.plot([x, x], [0.20, 0.845], color="#BBBBBB", lw=1.0, ls=(0, (4, 3)), zorder=0)

    steps = [
        (0.80, "① GET /.well-known/agent-card.json", "返回 Agent Card（skills、supportedInterfaces、securitySchemes）", BLUE),
        (0.725, "② POST /rpc — SendMessage", '\'{"jsonrpc":"2.0","id":1,"method":"SendMessage","params":{"message":{…}}}\'', BLUE),
        (0.65, '③ 200 OK → {"task": …, state=COMPLETED}', '一次性返回：Task + artifacts + history（或 {"message": …} 直接答复）', ORANGE),
        (0.575, "④ POST /rpc — SendStreamingMessage（Accept: text/event-stream）", "长任务改走流：一个请求，换回一条服务端持有的 SSE 流", BLUE),
    ]
    for y, label, note, color in steps:
        left_to_right = label.startswith("①") or label.startswith("②") or label.startswith("④")
        arrow(ax, cx if left_to_right else sx, y, sx if left_to_right else cx, y, "", color=color)
        ax.text(0.5, y + 0.012, label, ha="center", fontsize=8.6, weight="bold", color="#333333")
        ax.text(0.5, y - 0.026, note, ha="center", fontsize=7.6, color=GREY)

    # ⑤ SSE exchange: request down, frames back up, with room for frame payloads
    arrow(ax, cx, 0.505, sx, 0.505, "", color=BLUE)
    arrow(ax, sx, 0.415, cx, 0.415, "", color=ORANGE)
    ax.text(0.5, 0.528, "⑤ text/event-stream：每个 data: 帧一个 JSON-RPC 包", ha="center", fontsize=8.6, weight="bold", color="#333333")
    frames = [
        'data: {"jsonrpc":"2.0","id":2,"result":{"statusUpdate":  {"status":{"state":"TASK_STATE_WORKING"}}}}',
        'data: {"jsonrpc":"2.0","id":2,"result":{"artifactUpdate":{"artifact":{"parts":[{"text":"分片1"}]}}}}',
        'data: {"jsonrpc":"2.0","id":2,"result":{"statusUpdate":  {"status":{"state":"TASK_STATE_COMPLETED"}}}}',
    ]
    for i, fr in enumerate(frames):
        ax.text(0.5, 0.483 - i * 0.021, fr, ha="center", fontsize=6.9, color=ORANGE, family=["Noto Sans Mono CJK SC", "DejaVu Sans Mono"])
    ax.text(0.5, 0.385, "流由服务端持有；客户端读到 EOF 即本次运行结束（断线则用 push-notification webhook 补投）",
            ha="center", fontsize=7.5, color=ORANGE)

    # state machine strip
    ax.text(0.03, 0.315, "Task 状态机（规范 §4.1.3）", fontsize=9.5, weight="bold")
    states = [
        ("SUBMITTED", GREY), ("WORKING", BLUE), ("INPUT_REQUIRED", VERM), ("AUTH_REQUIRED", VERM),
        ("COMPLETED", GREEN), ("FAILED", VERM), ("CANCELED", GREY), ("REJECTED", GREY),
    ]
    x = 0.03
    for name, color in states:
        w = 0.030 + len(name) * 0.0082
        interrupted = name in ("INPUT_REQUIRED", "AUTH_REQUIRED")
        box(ax, x, 0.25, w, 0.042, name, fc="white", ec=color, fs=7.6,
            lw=1.6 if interrupted else 1.0, rounding=0.012)
        x += w + 0.012
    ax.text(0.03, 0.215, "红框 = 可中断态（人审批 / 凭证升级后可恢复）；灰框 = 终态。HITL 在协议层就是一次状态迁移。",
            fontsize=7.8, color=GREY)

    # error strip
    box(ax, 0.03, 0.02, 0.94, 0.09,
        "错误模型：HTTP 恒为 200，错误在 JSON-RPC envelope 里  —  传输级 -32600..-32603（如 -32601 Method not found）\n"
        "A2A 应用级 -32001..-32099（如 -32001 TaskNotFoundError）；gRPC 绑定时同一模型用 google.rpc.Status 表达",
        fc="#FBFBFB", ec=GREY, fs=8)
    save(fig, "fig2_a2a_wire")


if __name__ == "__main__":
    fig1()
    fig2()
