import { describe, expect, it } from "vitest";
import type { Topic, TopicEdge } from "../types";
import { createTopicAt, getRelatedTopicIds, topicMatchesQuery } from "./topics";

const topics: Topic[] = [
  {
    id: "sliding-window",
    title: "滑动窗口最大值",
    summary: "单调队列维护窗口极值",
    kind: "problem",
    tags: ["deque", "leetcode"],
    position: { x: 80, y: 100 },
    size: { width: 240, height: 180 },
    body: "正文",
    assetRefs: [{ path: "algorithms/competitive/leetcode_239_sliding_window_max.cpp" }]
  },
  {
    id: "monotonic-queue",
    title: "单调队列模板",
    summary: "队列范式",
    kind: "paradigm",
    tags: ["deque"],
    position: { x: 420, y: 200 },
    size: { width: 220, height: 160 },
    body: "正文",
    assetRefs: []
  }
];

const edges: TopicEdge[] = [
  {
    id: "edge-1",
    source: "sliding-window",
    target: "monotonic-queue",
    kind: "same-pattern"
  }
];

describe("topic helpers", () => {
  it("finds related topics from incoming and outgoing edges", () => {
    expect(getRelatedTopicIds("sliding-window", edges)).toEqual(["monotonic-queue"]);
    expect(getRelatedTopicIds("monotonic-queue", edges)).toEqual(["sliding-window"]);
  });

  it("matches topics by title, summary, tags, kind, and referenced assets", () => {
    expect(topicMatchesQuery(topics[0], "滑动窗口")).toBe(true);
    expect(topicMatchesQuery(topics[0], "deque")).toBe(true);
    expect(topicMatchesQuery(topics[0], "leetcode_239")).toBe(true);
    expect(topicMatchesQuery(topics[0], "interview")).toBe(false);
  });

  it("creates a new topic at the requested board coordinates", () => {
    const topic = createTopicAt({ x: 320, y: 180 });

    expect(topic.title).toBe("未命名专题");
    expect(topic.position).toEqual({ x: 320, y: 180 });
    expect(topic.size).toEqual({ width: 240, height: 180 });
    expect(topic.assetRefs).toEqual([]);
  });
});
