import { render } from "@testing-library/react";
import type { Core, CytoscapeOptions } from "cytoscape";
import { describe, expect, it, vi } from "vitest";
import { CytoscapeBoard } from "./CytoscapeBoard";
import type { Topic, TopicEdge } from "../types";

const topics: Topic[] = [
  {
    id: "a",
    title: "A",
    summary: "topic A",
    kind: "problem",
    tags: [],
    position: { x: 100, y: 100 },
    size: { width: 240, height: 180 },
    body: "",
    assetRefs: []
  }
];

const edges: TopicEdge[] = [];

describe("CytoscapeBoard lifecycle", () => {
  it("does not destroy and recreate cytoscape when parent callbacks change", () => {
    const fakeCy = createFakeCy();
    const createCy = vi.fn((_options: CytoscapeOptions) => fakeCy as unknown as Core);

    const firstClick = vi.fn();
    const { rerender } = render(
      <CytoscapeBoard
        topics={topics}
        edges={edges}
        focusedTopicId="a"
        editMode={false}
        onEdgeClick={vi.fn()}
        onTopicContextMenu={vi.fn()}
        onTopicClick={firstClick}
        onTopicDoubleClick={vi.fn()}
        onBlankContextMenu={vi.fn()}
        createCy={createCy}
      />
    );

    rerender(
      <CytoscapeBoard
        topics={topics}
        edges={edges}
        focusedTopicId="a"
        editMode={false}
        onEdgeClick={vi.fn()}
        onTopicContextMenu={vi.fn()}
        onTopicClick={vi.fn()}
        onTopicDoubleClick={vi.fn()}
        onBlankContextMenu={vi.fn()}
        createCy={createCy}
      />
    );

    expect(createCy).toHaveBeenCalledTimes(1);
    expect(fakeCy.add).toHaveBeenCalled();
  });

  it("does not move nodes when focus changes", () => {
    const fakeCy = createFakeCy();
    const createCy = vi.fn((_options: CytoscapeOptions) => fakeCy as unknown as Core);

    const { rerender } = render(
      <CytoscapeBoard
        topics={twoTopics}
        edges={twoTopicEdges}
        focusedTopicId="a"
        editMode={false}
        onEdgeClick={vi.fn()}
        onTopicContextMenu={vi.fn()}
        onTopicClick={vi.fn()}
        onTopicDoubleClick={vi.fn()}
        onBlankContextMenu={vi.fn()}
        createCy={createCy}
      />
    );
    fakeCy.layout.mockClear();

    rerender(
      <CytoscapeBoard
        topics={twoTopics}
        edges={twoTopicEdges}
        focusedTopicId="b"
        editMode={false}
        onEdgeClick={vi.fn()}
        onTopicContextMenu={vi.fn()}
        onTopicClick={vi.fn()}
        onTopicDoubleClick={vi.fn()}
        onBlankContextMenu={vi.fn()}
        createCy={createCy}
      />
    );

    expect(fakeCy.layout).not.toHaveBeenCalled();
  });

  it("fires onBlankContextMenu when background is right-clicked", () => {
    const fakeCy = createFakeCy();
    const onBlankCtx = vi.fn();
    let cxttapCallback: ((event: { target: unknown; renderedPosition: { x: number; y: number } }) => void) | null = null;
    fakeCy.on = vi.fn((event: string, callback: unknown) => {
      if (event === "cxttap") cxttapCallback = callback as typeof cxttapCallback;
    });
    const createCy = vi.fn((_options: CytoscapeOptions) => fakeCy as unknown as Core);

    render(
      <CytoscapeBoard
        topics={topics}
        edges={edges}
        focusedTopicId={null}
        editMode={false}
        onTopicClick={vi.fn()}
        onTopicDoubleClick={vi.fn()}
        onEdgeClick={vi.fn()}
        onTopicContextMenu={vi.fn()}
        onBlankContextMenu={onBlankCtx}
        createCy={createCy}
      />
    );

    expect(cxttapCallback).not.toBeNull();
    cxttapCallback!({ target: fakeCy, renderedPosition: { x: 300, y: 200 } });
    expect(onBlankCtx).toHaveBeenCalledWith({ x: 300, y: 200 });
  });

  it("fires onEdgeClick when an edge is tapped", () => {
    const fakeCy = createFakeCy();
    const onEdgeCb = vi.fn();
    let tapCallback: ((event: { target: { id: () => string } }) => void) | null = null;
    fakeCy.on = vi.fn((event: string, _selector: unknown, callback: unknown) => {
      if (event === "tap") tapCallback = callback as typeof tapCallback;
      return fakeCy;
    });
    const createCy = vi.fn((_options: CytoscapeOptions) => fakeCy as unknown as Core);

    render(
      <CytoscapeBoard
        topics={topics}
        edges={edges}
        focusedTopicId={null}
        editMode={false}
        onTopicClick={vi.fn()}
        onTopicDoubleClick={vi.fn()}
        onEdgeClick={onEdgeCb}
        onTopicContextMenu={vi.fn()}
        onBlankContextMenu={vi.fn()}
        createCy={createCy}
      />
    );

    expect(tapCallback).not.toBeNull();
    tapCallback!({ target: { id: () => "edge-1" } });
    expect(onEdgeCb).toHaveBeenCalledWith("edge-1");
  });
});

function createFakeCy() {
  const nodes = [
    {
      id: () => "a",
      data: vi.fn()
    },
    {
      id: () => "b",
      data: vi.fn()
    }
  ];
  const collection = {
    remove: vi.fn(),
    grabify: vi.fn(),
    forEach: vi.fn((callback: (node: (typeof nodes)[number]) => void) => nodes.forEach(callback))
  };
  const edgeCollection = {
    forEach: vi.fn()
  };

  return {
    on: vi.fn(),
    destroy: vi.fn(),
    elements: vi.fn(() => collection),
    add: vi.fn(),
    nodes: vi.fn(() => collection),
    edges: vi.fn(() => edgeCollection),
    zoom: vi.fn(),
    pan: vi.fn(),
    width: vi.fn(() => 1200),
    height: vi.fn(() => 800),
    layout: vi.fn(() => ({ run: vi.fn() }))
  };
}

const twoTopics: Topic[] = [
  ...topics,
  {
    id: "b",
    title: "B",
    summary: "topic B",
    kind: "problem",
    tags: [],
    position: { x: 400, y: 100 },
    size: { width: 240, height: 180 },
    body: "",
    assetRefs: []
  }
];

const twoTopicEdges: TopicEdge[] = [
  {
    id: "edge-ab",
    source: "a",
    target: "b",
    kind: "related"
  }
];
