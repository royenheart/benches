"""Inject probability theory topics into web/public/data/topics.json.

Adds:
- 1 parent topic "Probability Theory" (id: math.probability)
- 3 child topics for ch00, ch02, ch14
- Edges connecting children to parent

Idempotent: re-running will skip topics / edges that already exist by id.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

TOPICS_PATH = Path(__file__).resolve().parent.parent.parent / "web" / "public" / "data" / "topics.json"

PARENT_ID = "math.probability"
PARENT_TITLE = "概率论专题"

CHILDREN = [
    {
        "id": "math.probability.ch00",
        "title": "ch00 · 概率是什么 + 工作流落地",
        "summary": "概率公理、numpy/scipy/sympy 工作流、default_rng(seed) 可复现范式、LLN 直觉与可视化。",
        "kind": "topic",
        "tags": ["probability", "RNG", "intro", "numpy", "sympy"],
        "chapter_path": "mathematics/probability/ch00-prob-intuition/",
        "color": "#ede9fe",
    },
    {
        "id": "math.probability.ch02",
        "title": "ch02 · 条件概率、贝叶斯定理、独立性",
        "summary": "条件概率定义、全概率公式、贝叶斯公式、Beta-Binomial 共轭、医疗 PPV 与垃圾邮件过滤器 cut-off。",
        "kind": "topic",
        "tags": ["probability", "bayes", "conjugate", "Beta", "PPV"],
        "chapter_path": "mathematics/probability/ch02-conditional-bayes/",
        "color": "#dbeafe",
    },
    {
        "id": "math.probability.ch14",
        "title": "ch14 · 变分推断、重参数化、ELBO 推导",
        "summary": "ELBO 两种分解、高斯对高斯 KL 闭合解、rsample trick、MNIST PyTorch VAE demo、β-VAE 拉锯。",
        "kind": "topic",
        "tags": ["probability", "bayes", "VAE", "ELBO", "PyTorch"],
        "chapter_path": "mathematics/probability/ch14-variational-VAE/",
        "color": "#dcfce7",
    },
]


def _topic_to_entry(t: dict, position: dict, size: dict) -> dict:
    body = (
        "**讲解** " + t["summary"] + "\n\n"
        f"[!asset:{t['chapter_path']}README.md]\n"
        f"[!asset:{t['chapter_path']}notebook.ipynb]\n"
    )
    return {
        "id": t["id"],
        "title": t["title"],
        "summary": t["summary"],
        "kind": t["kind"],
        "tags": t["tags"],
        "position": position,
        "size": size,
        "theme": {"color": t["color"]},
        "body": body,
        "assetRefs": [
            {"path": t["chapter_path"] + "README.md", "label": "章节速读"},
            {"path": t["chapter_path"] + "notebook.ipynb", "label": "讲解 Notebook"},
            {"path": t["chapter_path"] + "exercises.md", "label": "课后题"},
        ],
    }


def _parent_entry(position: dict) -> dict:
    body = (
        "**专题** 循循序晋渐进、章节独立可跑、对接工业 AI 的概率论教程。\n\n"
        "阶段 A 已交付 ch00、ch02、ch14 三章（垂直切片）。"
        "其余 16 章 + 2 附录分阶段产出。\n\n"
        "[!asset:mathematics/probability/README.md]\n"
    )
    return {
        "id": PARENT_ID,
        "title": PARENT_TITLE,
        "summary": "循循序晋渐进、章节独立、对接工业 AI 的概率论教程。",
        "kind": "topic",
        "tags": ["probability", "statistics", "course", "machine-learning"],
        "position": position,
        "size": {"width": 280, "height": 200},
        "theme": {"color": "#fef3c7"},
        "body": body,
        "assetRefs": [
            {"path": "mathematics/probability/README.md", "label": "课程索引"},
            {"path": "mathematics/probability/SUMMARY.md", "label": "进度总览"},
            {"path": "mathematics/probability/_assets/style-guide.md", "label": "符号约定"},
            {"path": "mathematics/probability/_assets/deps-guide.md", "label": "依赖与启动"},
        ],
    }


def _edge_entry(child_id: str) -> dict:
    return {
        "id": f"edge-{PARENT_ID}-{child_id}",
        "source": child_id,
        "target": PARENT_ID,
        "kind": "chapter",
        "label": "属于",
    }


def inject():
    data = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
    topics: list = data.get("topics", [])
    edges: list = data.get("edges", [])

    existing_topic_ids = {t["id"] for t in topics if "id" in t}
    existing_edge_ids = {e["id"] for e in edges if "id" in e}

    new_topics = []
    if PARENT_ID not in existing_topic_ids:
        new_topics.append(_parent_entry(position={"x": 1200, "y": 60}))
    # children laid out in a vertical column to the right of parent
    child_x = 1180
    child_y_start = 320
    child_step = 260
    for i, child in enumerate(CHILDREN):
        if child["id"] in existing_topic_ids:
            continue
        pos = {"x": child_x, "y": child_y_start + i * child_step}
        size = {"width": 260, "height": 200}
        new_topics.append(_topic_to_entry(child, pos, size))

    new_edges = []
    for child in CHILDREN:
        e = _edge_entry(child["id"])
        if e["id"] not in existing_edge_ids:
            new_edges.append(e)

    if not new_topics and not new_edges:
        print("Nothing to inject: all topics and edges already present.")
        return

    data["topics"] = topics + new_topics
    data["edges"] = edges + new_edges

    TOPICS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Injected {len(new_topics)} topics and {len(new_edges)} edges.")
    print(f"Total now: {len(data['topics'])} topics, {len(data['edges'])} edges.")


if __name__ == "__main__":
    inject()