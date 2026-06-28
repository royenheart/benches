import { useState } from "react";
import MDEditor from "@uiw/react-md-editor";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { usePyodide } from "../lib/pyodide";

export interface NotebookCell {
  type: string;
  source: string;
}

export function parseNotebookCells(raw: string): NotebookCell[] {
  try {
    const nb = JSON.parse(raw);
    return (Array.isArray(nb.cells) ? nb.cells : [])
      .map((c: { cell_type: string; source: string | string[] }) => ({
        type: c.cell_type,
        source: Array.isArray(c.source) ? c.source.join("") : String(c.source ?? ""),
      }))
      .filter((c: { source: string }) => c.source.trim());
  } catch {
    // Fallback: old text-based format like [code]\n...content...
    const parts = raw.split(/\n(?=\[)/);
    return parts
      .map((c) => {
        const m = c.match(/^\[(\w+)\]([\s\S]*)/);
        return m ? { type: m[1], source: m[2].trim() } : { type: "code", source: c.trim() };
      })
      .filter((c) => c.source);
  }
}

export default function NotebookPreview({ raw }: { raw: string }) {
  const { ready, loading: pyLoading, runCode } = usePyodide();
  const [runState, setRunState] = useState<Record<number, string>>({});

  const cells = parseNotebookCells(raw);

  async function executeCell(index: number, code: string) {
    setRunState((s) => ({ ...s, [index]: "running" }));
    const output = await runCode(code);
    setRunState((s) => ({ ...s, [index]: output }));
  }

  if (!cells.length) {
    return (
      <div className="notebook-preview">
        <div className="notebook-py-status">无法解析 notebook 内容</div>
      </div>
    );
  }

  return (
    <div className="notebook-preview">
      {pyLoading ? (
        <div className="notebook-py-status">加载 Python 运行时 (Pyodide ~12MB)...</div>
      ) : null}
      {cells.map((cell, i) => {
        const isCode = cell.type === "code";
        const output = runState[i];
        return (
          <div key={i} className="notebook-cell">
            <div className="notebook-cell-bar">
              <span className="notebook-cell-type">{cell.type}</span>
              <span className="notebook-cell-index">In [{i + 1}]</span>
              {isCode ? (
                <button
                  type="button"
                  className="notebook-run-btn"
                  onClick={() => executeCell(i, cell.source)}
                  disabled={!ready || output === "running"}
                >
                  {output === "running" ? "..." : ready ? "▶ Run" : "加载中"}
                </button>
              ) : null}
            </div>
            {isCode ? (
              <SyntaxHighlighter
                language="python"
                style={oneDark}
                customStyle={{ margin: 0, borderRadius: 0, fontSize: 13 }}
              >
                {cell.source}
              </SyntaxHighlighter>
            ) : (
              <div className="notebook-md-cell">
                <MDEditor.Markdown
                  source={cell.source}
                  rehypePlugins={[[rehypeKatex, { output: "html" }]]}
                  remarkPlugins={[remarkMath]}
                />
              </div>
            )}
            {isCode && output && output !== "running" ? (
              <div className="notebook-cell-output">
                <pre>{output}</pre>
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
