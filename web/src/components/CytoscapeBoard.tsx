import cytoscape, { type Core } from "cytoscape";
import { useEffect, useMemo, useRef } from "react";
import type { Topic, TopicEdge } from "../types";

interface CytoscapeBoardProps {
  topics: Topic[];
  edges: TopicEdge[];
  focusedTopicId: string | null;
  editMode: boolean;
  onTopicClick: (topicId: string) => void;
  onTopicDoubleClick: (topicId: string) => void;
  onEdgeClick: (edgeId: string) => void;
  onBlankContextMenu: (point: { x: number; y: number }) => void;
  createCy?: (options: cytoscape.CytoscapeOptions) => Core;
}

export function CytoscapeBoard({
  topics,
  edges,
  focusedTopicId,
  editMode,
  onTopicClick,
  onTopicDoubleClick,
  onEdgeClick,
  onBlankContextMenu,
  createCy = cytoscape
}: CytoscapeBoardProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const lastTapRef = useRef<{ id: string; time: number } | null>(null);
  const onTopicClickRef = useRef(onTopicClick);
  const onEdgeClickRef = useRef(onEdgeClick);
  const onTopicDoubleClickRef = useRef(onTopicDoubleClick);
  const onBlankContextMenuRef = useRef(onBlankContextMenu);
  const isTestEnvironment =
    (import.meta as ImportMeta & { env?: { MODE?: string } }).env?.MODE === "test";
  const rendererDisabled = isTestEnvironment && createCy === cytoscape;

  useEffect(() => {
    onTopicClickRef.current = onTopicClick;
    onTopicDoubleClickRef.current = onTopicDoubleClick;
    onEdgeClickRef.current = onEdgeClick;
    onBlankContextMenuRef.current = onBlankContextMenu;
  }, [onBlankContextMenu, onEdgeClick, onTopicClick, onTopicDoubleClick]);

  const elements = useMemo(
    () => [
      ...topics.map((topic) => ({
        data: {
          id: topic.id,
          label: formatTopicLabel(topic),
          title: topic.title,
          kind: topic.kind,
          color: topic.theme?.color ?? "#ffffff"
        }
      })),
      ...edges.map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label ?? ""
        }
      }))
    ],
    [edges, topics]
  );

  useEffect(() => {
    if (rendererDisabled) {
      return;
    }

    if (!containerRef.current || cyRef.current) {
      return;
    }

    const cy = createCy({
      container: containerRef.current,
      autoungrabify: false,
      boxSelectionEnabled: false,
      style: [
        {
          selector: "core",
          style: {
            "active-bg-opacity": 0
          }
        },
        {
          selector: "node",
          style: {
            shape: "round-rectangle",
            width: 230,
            height: 158,
            "background-color": "data(color)",
            "background-opacity": 0.98,
            "border-width": 5,
            "border-color": "#111827",
            "border-opacity": 1,
            label: "data(label)",
            "text-wrap": "wrap",
            "text-max-width": 150,
            "text-valign": "center",
            "text-halign": "center",
            color: "#111827",
            "font-family": "Inter, system-ui, sans-serif",
            "font-size": 14,
            "font-weight": 800,
            "line-height": 1.35,
            "overlay-opacity": 0,
            "underlay-color": "#111827",
            "underlay-padding": 6,
            "underlay-opacity": 0.08
          }
        },
        {
          selector: "node[?focused]",
          style: {
            "border-color": "#ef4444",
            "border-width": 8,
            "background-color": "#fff1f2",
            "underlay-color": "#ef4444",
            "underlay-padding": 18,
            "underlay-opacity": 0.2,
            opacity: 1
          }
        },
        {
          selector: "node[?related]",
          style: {
            "border-color": "#14b8a6",
            "border-width": 7,
            "underlay-color": "#14b8a6",
            "underlay-padding": 14,
            "underlay-opacity": 0.16,
            opacity: 1
          }
        },
        {
          selector: "node[?dimmed]",
          style: {
            opacity: 0.32,
            "border-color": "#94a3b8",
            "underlay-opacity": 0
          }
        },
        {
          selector: "edge",
          style: {
            width: 3,
            "line-color": "#475569",
            "target-arrow-color": "#475569",
            "curve-style": "bezier",
            opacity: 0.42,
            label: "data(label)",
            "font-size": 11,
            color: "#334155",
            "text-background-color": "#f8fafc",
            "text-background-opacity": 1,
            "text-background-padding": 3
          }
        },
        {
          selector: "edge[?highlighted]",
          style: {
            width: 8,
            "line-color": "#111827",
            "target-arrow-color": "#111827",
            "font-size": 12,
            "font-weight": 800,
            opacity: 1
          }
        },
        {
          selector: "edge[?dimmed]",
          style: {
            opacity: 0.12,
            width: 2,
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8"
          }
        }
      ] as unknown as cytoscape.StylesheetCSS[]
    });

    cy.on("tap", "node", (event) => {
      const id = event.target.id();
      const now = Date.now();
      const lastTap = lastTapRef.current;
      if (lastTap && lastTap.id === id && now - lastTap.time < 320) {
        onTopicDoubleClickRef.current(id);
        lastTapRef.current = null;
        return;
      }

      lastTapRef.current = { id, time: now };
      onTopicClickRef.current(id);
    });


    cy.on("tap", "edge", (event) => {
      const edgeId = event.target.id();
      onEdgeClickRef.current(edgeId);
    });
    cy.on("cxttap", (event) => {
      if (event.target === cy) {
        onBlankContextMenuRef.current(event.renderedPosition);
      }
    });

    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [createCy, rendererDisabled]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }

    cy.elements().remove();
    cy.add(elements);
    cy.nodes().grabify();
    applyInitialBoardState(cy, focusedTopicId, edges);
  }, [elements]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !focusedTopicId) {
      return;
    }

    applyNodeHighlights(cy, focusedTopicId, edges);
  }, [edges, focusedTopicId, topics]);

  return (
    <div
      ref={containerRef}
      className="cytoscape-board"
      data-testid="cytoscape-board"
      data-layout-editable={editMode ? "true" : "false"}
      data-layout-engine="cytoscape"
      data-layout-animate={focusedTopicId ? "true" : "false"}
    />
  );
}

function applyNodeHighlights(cy: Core, focusedTopicId: string, edges: TopicEdge[]) {
  const relatedTopicIds = new Set(
    edges.flatMap((edge) =>
      edge.source === focusedTopicId ? [edge.target] : edge.target === focusedTopicId ? [edge.source] : []
    )
  );

  cy.nodes().forEach((node) => {
    const focused = node.id() === focusedTopicId;
    const related = relatedTopicIds.has(node.id());
    node.data("focused", focused);
    node.data("related", related);
    node.data("dimmed", !focused && !related);
  });
  cy.edges().forEach((edge) => {
    const highlighted = edge.source().id() === focusedTopicId || edge.target().id() === focusedTopicId;
    edge.data("highlighted", highlighted);
    edge.data("dimmed", !highlighted);
  });
}

function applyInitialBoardState(cy: Core, focusedTopicId: string | null, edges: TopicEdge[]) {
  if (focusedTopicId) {
    applyNodeHighlights(cy, focusedTopicId, edges);
  }
  cy.zoom(1);
  cy.pan({ x: 0, y: 0 });
  cy.layout({
    name: "circle",
    fit: true,
    padding: 150,
    avoidOverlap: true,
    spacingFactor: 1.25,
    animate: false
  }).run();
}

function formatTopicLabel(topic: Topic) {
  const title = wrapLabelText(topic.title, 12, 24);
  const summary = wrapLabelText(topic.summary || "暂无概要", 14, 34);
  return `${title}\n${summary}`;
}

function wrapLabelText(text: string, lineLength: number, maxChars: number) {
  const chars = Array.from(text.length > maxChars ? `${text.slice(0, maxChars - 1)}…` : text);
  const lines: string[] = [];
  for (let index = 0; index < chars.length; index += lineLength) {
    lines.push(chars.slice(index, index + lineLength).join(""));
  }
  return lines.join("\n");
}
