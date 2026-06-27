import type { BoardData } from "../types";

export const defaultData: BoardData = {
  topics: [
    {
      id: "sliding-window-max",
      title: "滑动窗口最大值",
      summary: "用单调队列维护窗口内最大值，适合作为队列范式入口。",
      kind: "problem",
      tags: ["deque", "leetcode", "monotonic-queue"],
      position: { x: 120, y: 130 },
      size: { width: 270, height: 210 },
      theme: { color: "#fef3c7" },
      body: "专题解析 LeetCode 239：维护一个下标单调递减的双端队列，队首始终是当前窗口最大值。",
      assetRefs: [
        {
          path: "algorithms/competitive/leetcode_239_sliding_window_max.cpp",
          label: "C++ 题解"
        },
        {
          path: "algorithms/competitive/leetcode_239_sliding_window_max_learning.ipynb",
          label: "学习笔记"
        }
      ]
    },
    {
      id: "monotonic-queue",
      title: "单调队列模板",
      summary: "抽象出窗口极值、过期元素删除和候选集维护。",
      kind: "paradigm",
      tags: ["deque", "template"],
      position: { x: 570, y: 300 },
      size: { width: 220, height: 260 },
      theme: { color: "#dbeafe" },
      body: "把题目拆成三个动作：弹出过期下标、维护候选单调性、读取队首答案。",
      assetRefs: []
    },
    {
      id: "minimum-window",
      title: "最小覆盖子串",
      summary: "滑动窗口的计数变体，强调何时扩张与收缩。",
      kind: "problem",
      tags: ["sliding-window", "hash"],
      position: { x: 850, y: 150 },
      size: { width: 250, height: 180 },
      theme: { color: "#dcfce7" },
      body: "专题解析 LeetCode 76：用计数表刻画窗口是否满足目标字符需求。",
      assetRefs: [
        {
          path: "algorithms/competitive/leetcode_76_min_cover_substr.cpp",
          label: "C++ 题解"
        }
      ]
    }
  ],
  edges: [
    {
      id: "edge-sliding-queue",
      source: "sliding-window-max",
      target: "monotonic-queue",
      kind: "same-pattern",
      label: "范式"
    },
    {
      id: "edge-sliding-minimum-window",
      source: "sliding-window-max",
      target: "minimum-window",
      kind: "variant",
      label: "滑窗变体"
    }
  ]
};
