import { act, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import NotebookPreview, { parseNotebookCells } from "./NotebookPreview";

const mockUsePyodide = vi.fn();
vi.mock("../lib/pyodide", () => ({
  usePyodide: () => mockUsePyodide(),
}));

function setPyodideReady() {
  mockUsePyodide.mockReturnValue({
    ready: true,
    loading: false,
    error: null,
    runCode: vi.fn().mockResolvedValue("mock output"),
  });
}

function setPyodideLoading() {
  mockUsePyodide.mockReturnValue({
    ready: false,
    loading: true,
    error: null,
    runCode: vi.fn(),
  });
}

function makeNbJson(cells: { cell_type: string; source: string[] }[]) {
  return JSON.stringify({ cells });
}

// Each source line in real ipynb includes its own \n
function line(s: string) { return s + "\n"; }

describe("parseNotebookCells", () => {
  it("parses valid ipynb JSON with code and markdown cells", () => {
    const raw = makeNbJson([
      { cell_type: "markdown", source: [line("# Hello")] },
      { cell_type: "code", source: [line("print(1)")] },
      { cell_type: "code", source: [line("x = 2"), line("print(x)")] },
    ]);
    const cells = parseNotebookCells(raw);
    expect(cells).toHaveLength(3);
    expect(cells[0]).toEqual({ type: "markdown", source: "# Hello\n" });
    expect(cells[1]).toEqual({ type: "code", source: "print(1)\n" });
    expect(cells[2]).toEqual({ type: "code", source: "x = 2\nprint(x)\n" });
  });

  it("joins multi-line source arrays", () => {
    const raw = makeNbJson([
      { cell_type: "code", source: [line("a = 1"), line("b = 2"), line("print(a + b)")] },
    ]);
    const cells = parseNotebookCells(raw);
    expect(cells[0].source).toBe("a = 1\nb = 2\nprint(a + b)\n");
  });

  it("returns empty array for empty notebook", () => {
    const raw = makeNbJson([]);
    expect(parseNotebookCells(raw)).toHaveLength(0);
  });

  it("filters out cells with only whitespace source", () => {
    const raw = makeNbJson([
      { cell_type: "code", source: ["  "] },
      { cell_type: "code", source: [line("print(1)")] },
    ]);
    const cells = parseNotebookCells(raw);
    expect(cells).toHaveLength(1);
    expect(cells[0].type).toBe("code");
    expect(cells[0].source).toBe("print(1)\n");
  });
});

describe("NotebookPreview component", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders cells with cell type labels", () => {
    setPyodideReady();
    const raw = makeNbJson([
      { cell_type: "markdown", source: [line("# Title")] },
      { cell_type: "code", source: [line("print(1)")] },
    ]);
    render(<NotebookPreview raw={raw} />);
    expect(screen.getByText("markdown")).toBeDefined();
    expect(screen.getByText("code")).toBeDefined();
  });

  it("renders In[] index labels", () => {
    setPyodideReady();
    const raw = makeNbJson([
      { cell_type: "markdown", source: [line("# Title")] },
      { cell_type: "code", source: [line("print(1)")] },
    ]);
    render(<NotebookPreview raw={raw} />);
    expect(screen.getByText("In [1]")).toBeDefined();
    expect(screen.getByText("In [2]")).toBeDefined();
  });

  it("renders Run button for code cells but not markdown cells", () => {
    setPyodideReady();
    const raw = makeNbJson([
      { cell_type: "markdown", source: [line("# Title")] },
      { cell_type: "code", source: [line("print(1)")] },
    ]);
    render(<NotebookPreview raw={raw} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(1);
    expect(buttons[0].textContent).toBe("▶ Run");
  });

  it("shows loading text when pyodide is not ready", () => {
    setPyodideLoading();
    const raw = makeNbJson([{ cell_type: "code", source: [line("print(1)")] }]);
    render(<NotebookPreview raw={raw} />);
    const btn = screen.getByRole("button");
    expect(btn.textContent).toBe("加载中");
  });

  it("disables Run button when pyodide is not ready", () => {
    setPyodideLoading();
    const raw = makeNbJson([{ cell_type: "code", source: [line("print(1)")] }]);
    render(<NotebookPreview raw={raw} />);
    const btn = screen.getByRole("button");
    expect(btn.hasAttribute("disabled")).toBe(true);
  });

  it("renders markdown cells with MDEditor not SyntaxHighlighter", () => {
    setPyodideReady();
    const raw = makeNbJson([
      { cell_type: "markdown", source: [line("# Hello World")] },
    ]);
    const { container } = render(<NotebookPreview raw={raw} />);
    // Markdown cells should use .wmde-markdown (MDEditor), not dark code theme
    expect(container.querySelector(".wmde-markdown")).toBeTruthy();
  });

  it("renders code cells with SyntaxHighlighter", () => {
    setPyodideReady();
    const raw = makeNbJson([
      { cell_type: "code", source: [line("print(1)")] },
    ]);
    const { container } = render(<NotebookPreview raw={raw} />);
    // Code cells should have a <pre> from SyntaxHighlighter
    expect(container.querySelector(".notebook-cell pre")).toBeTruthy();
  });
});
