#!/usr/bin/env python3
"""Teaching figure for the memory chapter: the three-plane org-memory architecture.

One diagram (Okabe-Ito palette, Noto Sans CJK SC, 300 DPI PNG + vector PDF):
org truth plane (human-governed) / governed memory plane (agent-facing) /
private per-agent plane, with read paths, the promotion gate, and anti-decay notes.

Run: python gen_figures.py   (outputs land next to this script)
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
        "figure.facecolor": "white",
    }
)

BLUE, ORANGE, GREEN, PURPLE, GREY, VERM = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#7F7F7F",
    "#D55E00",
)


def box(ax, x, y, w, h, text, fc="#FFFFFF", ec=GREY, fs=8.5, lw=1.2, weight="normal", rounding=0.05):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.008,rounding_size={rounding}",
            fc=fc, ec=ec, lw=lw, zorder=2,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight=weight, zorder=3)


def arrow(ax, x1, y1, x2, y2, text="", color=GREY, fs=7.5, ls="-", text_dy=0.012, text_dx=0.0, lw=1.5):
    ax.add_patch(
        FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, color=color, lw=lw, ls=ls, zorder=1)
    )
    if text:
        ax.text((x1 + x2) / 2 + text_dx, (y1 + y2) / 2 + text_dy, text, ha="center", fontsize=fs, color=color)


def fig1():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.965, "记忆三平面：组织级 agent 记忆架构", fontsize=13, weight="bold")
    ax.text(0.02, 0.928, "证据：2025-26 全部严肃共享记忆系统收敛于「私有层 + 受治理共享层 + 晋升闸门」；四种失效全是治理失败而非检索失败", fontsize=8.2, color=GREY)

    # ---- Plane 1: org truth (human-governed)
    box(ax, 0.02, 0.72, 0.96, 0.17, "", fc="#FBF7EF", ec=ORANGE, lw=1.6, rounding=0.02)
    ax.text(0.04, 0.862, "① 组织真相平面（人治理）", fontsize=10, weight="bold", color=VERM)
    box(ax, 0.04, 0.745, 0.27, 0.09, "git ADR/RFC 库\nMADR 格式 + 生命周期状态\nDocDag CI 图不变量检查", fc="white", ec=VERM, fs=7.8)
    box(ax, 0.37, 0.745, 0.24, 0.09, "文档系统（创作面）\nNotion / 飞书 / wiki\n人写人维护", fc="white", ec=GREY, fs=7.8)
    box(ax, 0.65, 0.745, 0.14, 0.09, "MCP 网关\n官方连接器\n只读为主", fc="white", ec=BLUE, fs=7.8)
    box(ax, 0.83, 0.745, 0.13, 0.09, "回写投影\n批准决策→文档\n（手动触发）", fc="white", ec=GREEN, fs=7.6)

    # ---- Plane 2: governed memory plane
    box(ax, 0.02, 0.40, 0.96, 0.26, "", fc="#EFF5FA", ec=BLUE, lw=1.6, rounding=0.02)
    ax.text(0.04, 0.625, "② 受治理记忆平面（agent 用的底座，cloud-agent §13.2）", fontsize=10, weight="bold", color=BLUE)
    box(ax, 0.04, 0.515, 0.30, 0.085, "Postgres 事件日志 episodes\nappend-only 事实源\n单写入 choke point（脱敏+污点）", fc="white", ec=BLUE, fs=7.6)
    box(ax, 0.37, 0.515, 0.24, 0.085, "投影（可重建）\nfacts 时间图谱 / 向量 / BM25\n失效不删除（Graphiti 式）", fc="white", ec=BLUE, fs=7.6)
    box(ax, 0.64, 0.515, 0.14, 0.085, "晋升闸门\nproposed\n→人审→approved", fc="white", ec=VERM, fs=7.6, lw=1.6)
    box(ax, 0.81, 0.515, 0.15, 0.085, "MCP memory server\n所有 agent 的\n统一读取面", fc="white", ec=GREEN, fs=7.6)

    # ---- Plane 3: private per-agent
    box(ax, 0.02, 0.10, 0.96, 0.22, "", fc="#F5F5F5", ec=GREY, lw=1.4, rounding=0.02)
    ax.text(0.04, 0.285, "③ 私有平面（每 agent 自维护、会腐化）", fontsize=10, weight="bold", color=GREY)
    for i, name in enumerate(["agent A 的记忆", "agent B 的记忆", "agent C 的记忆"]):
        box(ax, 0.06 + i * 0.24, 0.14, 0.20, 0.10, f"{name}\nA-MEM / Mem0 式\n自维护 + 按使用加权遗忘", fc="white", ec=GREY, fs=7.6)

    # ---- Arrows: read paths (dashed), promotion (bold), writeback
    arrow(ax, 0.72, 0.745, 0.885, 0.60, "读（只读）", color=BLUE, ls=(0, (4, 3)), text_dx=0.03)
    arrow(ax, 0.885, 0.60, 0.72, 0.745, "", color=BLUE, ls=(0, (4, 3)))
    arrow(ax, 0.885, 0.515, 0.885, 0.24, "MCP 读取 /\n决策前置检索", color=GREEN, ls=(0, (4, 3)), text_dx=0.055)
    arrow(ax, 0.30, 0.24, 0.64, 0.515, "晋升：提议 → 评审 → 提交（组织域永远不接受 agent 直写）", color=VERM, lw=2.2, text_dy=0.02)
    arrow(ax, 0.71, 0.515, 0.44, 0.745, "批准决策沉淀为 ADR", color=GREEN, ls=(0, (4, 3)), text_dx=-0.06)

    ax.text(
        0.02, 0.03,
        "防腐化四件套：全记录溯源（谁写/哪个会话/污点等级） · 晋升需验证（CoMem） · 失效用时间作废而非删除（Zep） · 周期重基线隔离断源记录（ArgusFleet 式活体探测）",
        fontsize=7.8, color=GREY,
    )

    for ext in ("png", "pdf"):
        path = HERE / f"fig1_memory_planes.{ext}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(f"wrote {path}")
    plt.close(fig)


if __name__ == "__main__":
    fig1()
