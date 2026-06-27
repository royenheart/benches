import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import type { Asset, BoardData } from "./types";
import type { Core, CytoscapeOptions } from "cytoscape";

const data: BoardData = {
  topics: [
    {
      id: "sliding-window",
      title: "滑动窗口最大值",
      summary: "单调队列维护窗口极值",
      kind: "problem",
      tags: ["deque"],
      position: { x: 80, y: 100 },
      size: { width: 240, height: 180 },
      body: "详细解析内容",
      assetRefs: []
    },
    {
      id: "monotonic-queue",
      title: "单调队列模板",
      summary: "相关范式",
      kind: "paradigm",
      tags: ["deque"],
      position: { x: 420, y: 210 },
      size: { width: 220, height: 160 },
      body: "模板内容",
      assetRefs: []
    }
  ],
  edges: [
    {
      id: "edge-1",
      source: "sliding-window",
      target: "monotonic-queue",
      kind: "same-pattern"
    }
  ]
};

const assets: Asset[] = [
  {
    path: "algorithms/competitive/leetcode_239_sliding_window_max.cpp",
    name: "leetcode_239_sliding_window_max.cpp",
    ext: ".cpp",
    type: "source",
    domain: "algorithms",
    previewable: true
  }
];

describe("App board interactions", () => {
  it("single-clicking a topic focuses it and marks related cards", () => {
    render(<App initialData={data} />);

    fireEvent.click(screen.getByRole("button", { name: /滑动窗口最大值/ }));

    const focusedCard = screen.getByRole("button", { name: /滑动窗口最大值/ });
    expect(focusedCard).toHaveAttribute(
      "data-focused",
      "true"
    );
    expect(screen.getByRole("button", { name: /单调队列模板/ })).toHaveAttribute(
      "data-related",
      "true"
    );
    expect(screen.getByTestId("cytoscape-board")).toHaveAttribute("data-layout-engine", "cytoscape");
    expect(screen.getByTestId("cytoscape-board")).toHaveAttribute("data-layout-animate", "true");
  });

  it("double-clicking opens full-page reading detail in read mode and IDE workbench in edit mode", () => {
    render(<App initialData={data} />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /滑动窗口最大值/ }));
    expect(screen.getByRole("dialog", { name: "专题阅读" })).toHaveClass("reader-page");

    fireEvent.click(screen.getByRole("button", { name: "关闭" }));
    fireEvent.click(screen.getByRole("button", { name: "编辑模式" }));
    fireEvent.doubleClick(screen.getByRole("button", { name: /滑动窗口最大值/ }));

    expect(screen.getByRole("dialog", { name: "专题编辑工作台" })).toBeInTheDocument();
    expect(screen.getByText("资产窗口")).toBeInTheDocument();
  });


  it("lets the edit drawer search and add repository assets", () => {
    render(<App initialData={data} initialAssets={assets} initialMode="edit" />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /单调队列模板/ }));
    fireEvent.change(screen.getByLabelText("资产搜索"), { target: { value: "239" } });
    fireEvent.dragStart(screen.getByRole("button", { name: /拖动 leetcode_239_sliding_window_max.cpp/ }));
    fireEvent.drop(screen.getByTestId("topic-editor-canvas"), { clientX: 160, clientY: 120 });

    expect(screen.getAllByText("leetcode_239_sliding_window_max.cpp")).toHaveLength(2);
  });

  it("shows edge manager with existing edges in edit workbench", () => {
    render(<App initialData={data} initialMode="edit" />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /滑动窗口最大值/ }));

    expect(screen.getByText("关联专题")).toBeInTheDocument();
    expect(screen.getByText("same-pattern")).toBeInTheDocument();
    expect(screen.getAllByText("单调队列模板")).toHaveLength(2);
  });

  it("shows add edge form with disabled button when no target selected", () => {
    render(<App initialData={data} initialAssets={assets} initialMode="edit" />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /单调队列模板/ }));

    expect(screen.getByRole("button", { name: "添加关联" })).toBeDisabled();
    expect(screen.getByText("选择关联专题")).toBeInTheDocument();
  });

  it("deletes an existing edge in edit mode", () => {
    render(<App initialData={data} initialMode="edit" />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /滑动窗口最大值/ }));

    const deleteButtons = screen.getAllByRole("button", { name: "×" });
    expect(deleteButtons).toHaveLength(1);

    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText("暂无关联")).toBeInTheDocument();
  });

  it("saves edited topic data to the local API", () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true })
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App initialData={data} initialAssets={assets} initialMode="edit" />);

    fireEvent.doubleClick(screen.getByRole("button", { name: /单调队列模板/ }));
    fireEvent.change(screen.getByLabelText("标题"), { target: { value: "单调队列 Topdown" } });
    fireEvent.click(screen.getByRole("button", { name: "保存专题" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/topics",
      expect.objectContaining({
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: expect.stringContaining("单调队列 Topdown")
      })
    );

    vi.unstubAllGlobals();
  });

  it("disables edit mode when rendered as a static-only board", () => {
    render(<App initialData={data} initialAssets={assets} staticOnly />);

    expect(screen.getByRole("button", { name: "编辑模式" })).toBeDisabled();
  });

  it("auto-disables edit mode when only static JSON data is available", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url === "/data/topics.json") {
        return { ok: true, json: async () => data };
      }
      if (url === "/data/assets.json") {
        return { ok: true, json: async () => assets };
      }
      return { ok: false, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "编辑模式" })).toBeDisabled();
    });

    vi.unstubAllGlobals();
  });

  it("prevents browser context menu on board right-click", () => {
    render(<App initialData={data} initialMode="edit" />);
    const boardEl = screen.getByTestId("topic-board");
    const spy = vi.spyOn(Event.prototype, "preventDefault");
    fireEvent.contextMenu(boardEl);
    expect(spy).toHaveBeenCalled();
    spy.mockRestore();
  });

  it("dismisses context menu when clicking on the board", () => {
    render(<App initialData={data} initialMode="edit" />);
    const boardEl = screen.getByTestId("topic-board");
    fireEvent.click(boardEl);
    expect(screen.queryByText("新增专题")).not.toBeInTheDocument();
    expect(screen.queryByText("删除专题")).not.toBeInTheDocument();
  });

  it("discards new topic when closing workbench without saving", async () => {
    const fakeCy = {
      on: vi.fn(),
      destroy: vi.fn(),
      elements: vi.fn(() => ({ remove: vi.fn() })),
      add: vi.fn(),
      nodes: vi.fn(() => ({ length: 0, forEach: vi.fn(), grabify: vi.fn() })),
      edges: vi.fn(() => ({ forEach: vi.fn() })),
      zoom: vi.fn(),
      pan: vi.fn(),
      width: vi.fn(() => 1200),
      height: vi.fn(() => 800),
      layout: vi.fn(() => ({ run: vi.fn() })),
    };
    let capturedCallback: ((evt: { target: unknown; renderedPosition: { x: number; y: number } }) => void) | null = null;
    fakeCy.on = vi.fn((...args: unknown[]) => {
      if (args[0] === "cxttap") capturedCallback = args[1] as typeof capturedCallback;
      return fakeCy;
    });
    const createCy = vi.fn((_opts: CytoscapeOptions) => fakeCy as unknown as Core);

    render(<App initialData={data} initialMode="edit" createCy={createCy} />);

    await waitFor(() => {
      expect(createCy).toHaveBeenCalled();
      expect(capturedCallback).not.toBeNull();
    });

    act(() => {
      capturedCallback!({ target: fakeCy, renderedPosition: { x: 400, y: 300 } });
    });
    expect(screen.getByText("新增专题")).toBeInTheDocument();

    fireEvent.click(screen.getByText("新增专题"));
    expect(screen.getAllByText("未命名专题").length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole("button", { name: "关闭" }));

    expect(screen.queryAllByText("未命名专题")).toHaveLength(0);
  });
});
