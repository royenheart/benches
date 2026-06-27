import type { Topic, TopicEdge } from "../types";

export function getRelatedTopicIds(topicId: string, edges: TopicEdge[]): string[] {
  const related = new Set<string>();

  for (const edge of edges) {
    if (edge.source === topicId) {
      related.add(edge.target);
    }
    if (edge.target === topicId) {
      related.add(edge.source);
    }
  }

  return [...related].sort();
}

export function topicMatchesQuery(topic: Topic, query: string): boolean {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  const fields = [
    topic.title,
    topic.summary,
    topic.kind,
    topic.body,
    ...topic.tags,
    ...topic.assetRefs.flatMap((asset) => [asset.path, asset.label ?? ""])
  ];

  return fields.some((field) => field.toLowerCase().includes(normalized));
}

export function createTopicAt(position: { x: number; y: number }): Topic {
  return {
    id: `topic-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
    title: "未命名专题",
    summary: "",
    kind: "note",
    tags: [],
    position,
    size: { width: 240, height: 180 },
    body: "",
    assetRefs: []
  };
}
