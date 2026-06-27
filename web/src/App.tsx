import { BookOpen, Edit3, Search } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { CytoscapeBoard } from "./components/CytoscapeBoard";
import { defaultData } from "./data/defaultData";
import { assetMatchesQuery } from "./lib/assets";
import { getRelatedTopicIds, topicMatchesQuery, createTopicAt } from "./lib/topics";
import type { Asset, BoardData, BoardMode, Topic } from "./types";
import MDEditor from "@uiw/react-md-editor";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { usePyodide } from "./lib/pyodide";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface AppProps {
  initialData?: BoardData;
  initialAssets?: Asset[];
  initialMode?: BoardMode;
  staticOnly?: boolean;
  createCy?: (options: import("cytoscape").CytoscapeOptions) => import("cytoscape").Core;
}

type PanelState =
  | { type: "none" }
  | { type: "read"; topicId: string }
  | { type: "edit"; topicId: string };

type ContextMenuState = | { type: "blank"; x: number; y: number; boardX: number; boardY: number } | { type: "topic"; topicId: string; x: number; y: number } | null;

export default function App({
  initialData,
  initialAssets,
  initialMode = "read",
  createCy,
  staticOnly = false
}: AppProps) {
  const [data, setData] = useState<BoardData>(initialData ?? defaultData);
  const [assets, setAssets] = useState<Asset[]>(initialAssets ?? []);
  const [apiAvailable, setApiAvailable] = useState(Boolean(initialData));
  const [mode, setMode] = useState<BoardMode>(staticOnly ? "read" : initialMode);
  const [query, setQuery] = useState("");
  const [focusedTopicId, setFocusedTopicId] = useState<string | null>(data.topics[0]?.id ?? null);
  const [focusedEdgeId, setFocusedEdgeId] = useState<string | null>(null);
  const [newTopicId, setNewTopicId] = useState<string | null>(null);
  const [panel, setPanel] = useState<PanelState>({ type: "none" });
  const [contextMenu, setContextMenu] = useState<ContextMenuState>(null);
  const [saveStatus, setSaveStatus] = useState("未保存");
  const canEdit = !staticOnly && apiAvailable;
  const autoSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (initialData) {
      return;
    }

    async function loadTopics() {
      try {
        const response = await fetch("/api/topics");
        if (response.ok) {
          setApiAvailable(true);
          const loaded = (await response.json()) as BoardData;
          setData(loaded);
          return;
        }
      } catch {
        // Fall back to static data below.
      }

      setApiAvailable(false);
      setMode("read");
      setData(await fetchJson<BoardData>(["/data/topics.json"], defaultData));
    }

    void loadTopics();
  }, [initialData]);

  useEffect(() => {
    if (initialAssets) {
      return;
    }

    fetchJson<Asset[]>(["/api/assets", "/data/assets.json"], [])
      .then((loaded) => setAssets(loaded))
      .catch(() => setAssets([]));
  }, [initialAssets]);

  const relatedTopicIds = useMemo(() => {
    return focusedTopicId ? getRelatedTopicIds(focusedTopicId, data.edges) : [];
  }, [data.edges, focusedTopicId]);

  const visibleTopics = useMemo(() => {
    return data.topics.filter((topic) => topicMatchesQuery(topic, query));
  }, [data.topics, query]);

  const activeTopic = useMemo(() => {
    if (panel.type === "none") {
      return null;
    }
    return data.topics.find((topic) => topic.id === panel.topicId) ?? null;
  }, [data.topics, panel]);

  function handleTopicClick(topicId: string) {
    setFocusedTopicId(topicId);
    setContextMenu(null);
  }

  function handleTopicDoubleClick(topicId: string) {
    setPanel({ type: mode === "edit" && canEdit ? "edit" : "read", topicId });
  }

  function handleEdgeClick(edgeId: string) {
    setFocusedEdgeId(edgeId);
    setFocusedTopicId(null);
    setContextMenu(null);
  }

  function handleTopicContextMenu(topicId: string, point: { x: number; y: number }) {
    if (mode !== "edit" || !canEdit) {
      setContextMenu(null);
      return;
    }
    setContextMenu({ type: "topic", topicId, x: point.x, y: point.y });
  }

  function addTopicFromContextMenu() {
    if (!contextMenu || contextMenu.type !== "blank") {
      return;
    }

    const topic = createTopicAt({ x: contextMenu.boardX, y: contextMenu.boardY });
    setData((current) => ({ ...current, topics: [...current.topics, topic] }));
    setFocusedTopicId(topic.id);
    setPanel({ type: "edit", topicId: topic.id });
    setNewTopicId(topic.id);
    setContextMenu(null);
  }

  function updateTopic(topicId: string, patch: Partial<Topic>) {
    setData((current) => ({
      ...current,
      topics: current.topics.map((topic) => (topic.id === topicId ? { ...topic, ...patch } : topic))
    }));
  }

  function addAssetRef(topicId: string, asset: Asset, position?: { x: number; y: number }) {
    const topic = data.topics.find((candidate) => candidate.id === topicId);
    if (!topic) {
      return;
    }

    if (topic.assetRefs.some((ref) => ref.path === asset.path)) {
      updateTopic(topicId, {
        assetRefs: topic.assetRefs.map((ref) =>
          ref.path === asset.path ? { ...ref, label: ref.label ?? asset.name, position } : ref
        )
      });
      return;
    }

    updateTopic(topicId, {
      assetRefs: [...topic.assetRefs, { path: asset.path, label: asset.name, position }]
    });
  }

  function generateEdgeId() {
    return `edge-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  }

  function deleteTopic(topicId: string) {
    setData((current) => ({
      ...current,
      topics: current.topics.filter((topic) => topic.id !== topicId),
      edges: current.edges.filter((edge) => edge.source !== topicId && edge.target !== topicId)
    }));
    setFocusedTopicId((current) => (current === topicId ? null : current));
    setFocusedEdgeId(null);
    setPanel((current) => (current.type !== "none" && current.topicId === topicId ? { type: "none" } : current));
    setContextMenu(null);
  }

  function addEdge(source: string, target: string, kind: import("./types").EdgeKind = "related", label?: string) {
    setData((current) => ({
      ...current,
      edges: [
        ...current.edges,
        { id: generateEdgeId(), source, target, kind, label }
      ]
    }));
  }

  function updateEdge(edgeId: string, patch: Partial<import("./types").TopicEdge>) {
    setData((current) => ({
      ...current,
      edges: current.edges.map((edge) => (edge.id === edgeId ? { ...edge, ...patch } : edge))
    }));
  }

  function deleteEdge(edgeId: string) {
    setData((current) => ({
      ...current,
      edges: current.edges.filter((edge) => edge.id !== edgeId)
    }));
  }

  async function saveTopics() {
    if (!canEdit) {
      return;
    }

    setSaveStatus("保存中...");
    const response = await fetch("/api/topics", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      setSaveStatus("保存失败");
      return;
    }

    setSaveStatus("已保存");
    setNewTopicId(null);
  }

  async function exportStaticData() {
    if (!canEdit) {
      return;
    }

    setSaveStatus("导出中...");
    const response = await fetch("/api/export", { method: "POST" });

    if (!response.ok) {
      setSaveStatus("导出失败");
      return;
    }

    setSaveStatus("已导出静态数据");
  }

  useEffect(() => {
    if (panel.type !== "edit" || !canEdit || activeTopic?.id === newTopicId) {
      return;
    }

    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        const response = await fetch("/api/topics", {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(data)
        });
        if (response.ok) {
          setSaveStatus("已自动保存");
        }
      } catch {
        /* ignore auto-save failures */
      }
    }, 2000);

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [data, panel, canEdit, activeTopic, newTopicId]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <label className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索专题 / 资产 / 标签"
          />
        </label>
        <div className="mode-toggle" aria-label="模式切换">
          <button
            type="button"
            aria-pressed={mode === "read"}
            onClick={() => setMode("read")}
            className={mode === "read" ? "active" : ""}
          >
            <BookOpen size={16} aria-hidden="true" />
            阅读模式
          </button>
          <button
            type="button"
            aria-pressed={mode === "edit"}
            disabled={!canEdit}
            onClick={() => canEdit && setMode("edit")}
            className={mode === "edit" ? "active" : ""}
          >
            <Edit3 size={16} aria-hidden="true" />
            编辑模式
          </button>
        </div>
      </header>

      <section
        className="topic-board"
        data-testid="topic-board"
        onContextMenu={(event) => event.preventDefault()}
        onClick={() => setContextMenu(null)}
      >
        <CytoscapeBoard
          createCy={createCy}
          topics={visibleTopics}
          edges={data.edges}
          focusedTopicId={focusedTopicId}
          editMode={mode === "edit" && canEdit}
          onTopicClick={handleTopicClick}
          onTopicDoubleClick={handleTopicDoubleClick}
          onEdgeClick={handleEdgeClick}
          onTopicContextMenu={handleTopicContextMenu}
          onBlankContextMenu={(point) => {
            if (mode !== "edit" || !canEdit) {
              setContextMenu(null);
              return;
            }
            setContextMenu({
              type: "blank",
              x: point.x,
              y: point.y,
              boardX: point.x,
              boardY: point.y
            });
          }}
        />
        {visibleTopics.map((topic) => {
          const focused = topic.id === focusedTopicId;
          const related = relatedTopicIds.includes(topic.id);
          return (
            <button
              key={topic.id}
              type="button"
              className="topic-accessible-node"
              aria-label={`${topic.title} ${topic.summary}`}
              data-focused={focused ? "true" : "false"}
              data-related={related ? "true" : "false"}
              onClick={() => handleTopicClick(topic.id)}
              onDoubleClick={() => handleTopicDoubleClick(topic.id)}
            >
              {topic.title}
            </button>
          );
        })}

        {contextMenu ? (
          <div className="context-menu" style={{ left: contextMenu.x, top: contextMenu.y }}>
            {contextMenu.type === "blank" ? (
              <button type="button" onClick={addTopicFromContextMenu}>
                新增专题
              </button>
            ) : contextMenu.type === "topic" ? (
              <button type="button" onClick={() => deleteTopic(contextMenu.topicId)}>
                删除专题
              </button>
            ) : null}
          </div>
        ) : null}
      </section>

      {activeTopic && panel.type === "read" ? (
        <TopicReadPage topic={activeTopic} onClose={() => setPanel({ type: "none" })} />
      ) : null}

      {activeTopic && panel.type === "edit" ? (
        <TopicEditWorkbench
          topic={activeTopic}
          allTopics={data.topics}
          edges={data.edges}
          onAddEdge={addEdge}
          onUpdateEdge={updateEdge}
          onDeleteEdge={deleteEdge}
          assets={assets}
          saveStatus={saveStatus}
          onClose={() => { if (activeTopic.id === newTopicId) { deleteTopic(activeTopic.id); setNewTopicId(null); } setPanel({ type: "none" }); }}
          onUpdate={(patch) => updateTopic(activeTopic.id, patch)}
          onAddAsset={(asset, position) => addAssetRef(activeTopic.id, asset, position)}
          onSave={saveTopics}
          onExport={exportStaticData}
        />
      ) : null}
    </main>
  );
}

async function fetchJson<T>(urls: string[], fallback: T): Promise<T> {
  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return response.json() as Promise<T>;
      }
    } catch {
      // Try the next source.
    }
  }
  return fallback;
}

function TopicReadPage({ topic, onClose }: { topic: Topic; onClose: () => void }) {
  return (
    <section className="reader-page" role="dialog" aria-label="专题阅读">
      <div className="reader-header">
        <div>
          <span className="eyebrow">专题阅读</span>
          <h1>{topic.title}</h1>
        </div>
        <button type="button" onClick={onClose}>
          关闭
        </button>
      </div>
      <p className="summary">{topic.summary}</p>
      <div className="tag-row">
        {topic.tags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>
      <MarkdownBody body={topic.body} />
    </section>
  );
}

function TopicEditWorkbench({
  allTopics,
  edges,
  onAddEdge,
  onUpdateEdge,
  onDeleteEdge,
  topic,
  assets,
  saveStatus,
  onClose,
  onUpdate,
  onAddAsset,
  onSave,
  onExport
}: {
  topic: Topic;
  assets: Asset[];
  saveStatus: string;
  onClose: () => void;
  allTopics: Topic[];
  edges: import("./types").TopicEdge[];
  onAddEdge: (source: string, target: string, kind?: import("./types").EdgeKind, label?: string) => void;
  onUpdateEdge: (edgeId: string, patch: Partial<import("./types").TopicEdge>) => void;
  onDeleteEdge: (edgeId: string) => void;
  onUpdate: (patch: Partial<Topic>) => void;
  onAddAsset: (asset: Asset, position?: { x: number; y: number }) => void;
  onSave: () => void;
  onExport: () => void;
}) {
  const [assetQuery, setAssetQuery] = useState("");
  const [draggedAsset, setDraggedAsset] = useState<Asset | null>(null);
  const editorCanvasRef = useRef<HTMLDivElement>(null);
  const visibleAssets = assets.filter((asset) => assetMatchesQuery(asset, assetQuery)).slice(0, 12);
  const topicEdges = edges.filter((edge) => edge.source === topic.id || edge.target === topic.id);
  const connectedTopicIds = new Set(topicEdges.flatMap((edge) => [edge.source, edge.target]));
  const availableTopics = allTopics.filter((candidate) => candidate.id !== topic.id && !connectedTopicIds.has(candidate.id));
  const [newEdgeTarget, setNewEdgeTarget] = useState("");
  const [newEdgeKind, setNewEdgeKind] = useState<import("./types").EdgeKind>("related");
  const [newEdgeLabel, setNewEdgeLabel] = useState("");

  function handleAddEdge() {
    if (!newEdgeTarget) {
      return;
    }
    onAddEdge(topic.id, newEdgeTarget, newEdgeKind, newEdgeLabel || undefined);
    setNewEdgeTarget("");
    setNewEdgeKind("related");
    setNewEdgeLabel("");
  }

  function insertAssetRef(assetPath: string) {
    const ta = document.querySelector(".md-source") as HTMLTextAreaElement | null;
    if (!ta) return;
    const ref = "\n[!asset:" + assetPath + "]\n";
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const before = (topic.body || "").slice(0, start);
    const after = (topic.body || "").slice(end);
    const newBody = before + ref + after;
    onUpdate({ body: newBody });
    requestAnimationFrame(() => {
      ta.focus();
      const pos = start + ref.length;
      ta.setSelectionRange(pos, pos);
    });
  }

  function dropAsset(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    if (!draggedAsset) {
      return;
    }

    const rect = editorCanvasRef.current?.getBoundingClientRect();
    onAddAsset(draggedAsset, {
      x: Math.max(18, Math.round(event.clientX - (rect?.left ?? 0))),
      y: Math.max(18, Math.round(event.clientY - (rect?.top ?? 0)))
    });
    setDraggedAsset(null);
  }

  return (
    <section className="edit-workbench" role="dialog" aria-label="专题编辑工作台">
      <div className="workbench-topbar">
        <div>
          <span className="eyebrow">专题编辑工作台</span>
          <h1>{topic.title}</h1>
        </div>
        <div className="edit-actions">
          <button type="button" onClick={onSave}>
            保存专题
          </button>
          <button type="button" onClick={onExport}>
            导出静态数据
          </button>
          <span>{saveStatus}</span>
          <button type="button" onClick={onClose}>
            关闭
          </button>
        </div>
      </div>

      <div className="workbench-grid">
        <section className="editor-window">
          <h2>专题编辑窗口</h2>
          <label>
            标题
            <input value={topic.title} onChange={(event) => onUpdate({ title: event.target.value })} />
          </label>
          <label>
            概要
            <textarea
              value={topic.summary}
              onChange={(event) => onUpdate({ summary: event.target.value })}
            />
          </label>
          <label>
            标签
            <input
              value={topic.tags.join(", ")}
              onChange={(event) =>
                onUpdate({
                  tags: event.target.value
                    .split(",")
                    .map((tag) => tag.trim())
                    .filter(Boolean)
                })
              }
            />
          </label>
          <label>
            正文（Markdown）
            <textarea
              className="md-source"
              style={{
                background: "#1e293b",
                color: "#e2e8f0",
                border: "2px solid #111827",
                borderRadius: 4,
                padding: "14px 16px",
                width: "100%",
                minHeight: 260,
                fontFamily: '"JetBrains Mono", "Fira Code", monospace',
                fontSize: 14,
                lineHeight: 1.7,
                resize: "vertical",
                tabSize: 2,
              }}
              value={topic.body || ""}
              onChange={(event) => onUpdate({ body: event.target.value })}
              placeholder="Markdown 撰写正文..."
              spellCheck={false}
            />
          </label>
          <div className="md-preview">
            <MarkdownBody body={topic.body || "*（暂无内容）*"} />
          </div>

        <section className="edge-manager">
          <h2>关联专题</h2>
          {topicEdges.length ? (
            <ul className="edge-list">
              {topicEdges.map((edge) => {
                const peerId = edge.source === topic.id ? edge.target : edge.source;
                const peer = allTopics.find((candidate) => candidate.id === peerId);
                return (
                  <li key={edge.id}>
                    <span className="edge-kind-label">{edge.kind}</span>
                    <span className="edge-peer-title">{peer?.title ?? peerId}</span>
                    <span className="edge-label-text">{edge.label ?? ""}</span>
                    <button type="button" onClick={() => onDeleteEdge(edge.id)} className="edge-delete-btn">
                      ×
                    </button>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="edge-empty">暂无关联</p>
          )}

          <div className="edge-add-form">
            <select value={newEdgeTarget} onChange={(event) => setNewEdgeTarget(event.target.value)}>
              <option value="">选择关联专题</option>
              {availableTopics.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.title}
                </option>
              ))}
            </select>
            <select value={newEdgeKind} onChange={(event) => setNewEdgeKind(event.target.value as import("./types").EdgeKind)}>
              <option value="related">相关</option>
              <option value="prerequisite">前置</option>
              <option value="variant">变体</option>
              <option value="same-pattern">同一范式</option>
              <option value="custom">自定义</option>
            </select>
            <input
              value={newEdgeLabel}
              onChange={(event) => setNewEdgeLabel(event.target.value)}
              placeholder="标签 (可选)"
            />
            <button type="button" onClick={handleAddEdge} disabled={!newEdgeTarget}>
              添加关联
            </button>
          </div>
        </section>
        </section>

        <aside className="asset-browser">
          <h2>资产窗口</h2>
          <label>
            资产搜索
            <input
              value={assetQuery}
              onChange={(event) => setAssetQuery(event.target.value)}
              placeholder="搜索路径、类型或目录"
            />
          </label>
          <div className="asset-list">
            {visibleAssets.map((asset) => (
              <button
                key={asset.path}
                type="button"
                // draggable
                // onDragStart
                onClick={() => insertAssetRef(asset.path)}
                aria-label={`插入 ${asset.name}`}
              >
                <strong>{asset.name}</strong>
                <span>
                  {asset.type} · {asset.domain}
                </span>
                <code>{asset.path}</code>
              </button>
            ))}
            {!visibleAssets.length ? <p>没有匹配的资产</p> : null}
          </div>
        </aside>
      </div>
    </section>
  );
}

function AssetRefs({ topic }: { topic: Topic }) {
  return (
    <section className="asset-refs">
      <h2>引用资产</h2>
      {topic.assetRefs.length ? (
        <ul>
          {topic.assetRefs.map((asset) => (
            <li key={asset.path}>
              <code>{asset.label ?? asset.path}</code>
              <span>{asset.path}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>暂无引用资产</p>
      )}
    </section>
  );
}

function MarkdownBody({ body }: { body: string }) {
  const pattern = /\[!asset:([^\]]+)\]/g;
  const segments: { type: "md" | "asset"; content: string }[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = pattern.exec(body)) !== null) {
    if (m.index > last) segments.push({ type: "md", content: body.slice(last, m.index) });
    segments.push({ type: "asset", content: m[1] });
    last = m.index + m[0].length;
  }
  if (last < body.length) segments.push({ type: "md", content: body.slice(last) });
  if (!segments.length) segments.push({ type: "md", content: body });

  return (
    <div className="markdown-body-wrap">
      {segments.map((seg, i) =>
        seg.type === "md" ? (
          <MDEditor.Markdown
            key={`md-${i}`}
            source={seg.content}
            rehypePlugins={[[rehypeKatex, { output: "html" }]]}
            remarkPlugins={[remarkMath]}
          />
        ) : (
          <AssetBlock key={`asset-${i}`} assetPath={seg.content} />
        )
      )}
    </div>
  );
}

function AssetBlock({ assetPath }: { assetPath: string }) {
  const [body, setBody] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancel = false;
    async function load() {
      setLoading(true);
      try {
        const r = await fetch(`/api/assets/preview?path=${encodeURIComponent(assetPath)}`);
        if (r.ok) {
          const d = await r.json() as { preview: string };
          if (!cancel) setBody(d.preview);
        }
      } catch { /* ignore */ }
      if (!cancel) setLoading(false);
    }
    void load();
    return () => { cancel = true; };
  }, [assetPath]);

  const name = assetPath.split("/").at(-1) ?? assetPath;
  const ext = (name.includes(".") ? name.slice(name.lastIndexOf(".")) : "").toLowerCase();

  return (
    <div className="asset-block-inline">
      <div className="asset-block-header">
        <code className="asset-block-path">{assetPath}</code>
      </div>
      <div className="asset-block-content">
        {loading ? (
          <p className="asset-block-loading">加载中...</p>
        ) : !body ? (
          <p className="asset-block-error">无法加载</p>
        ) : ext === ".ipynb" ? (
          <NotebookPreview raw={body} />
        ) : (
          <CodeBlock code={body} language={ext.slice(1)} />
        )}
      </div>
    </div>
  );
}

const LANG: Record<string, string> = {
  cpp: "cpp", cc: "cpp", cxx: "cpp", c: "c", cu: "cpp", cuh: "cpp",
  h: "c", hpp: "cpp", py: "python", rs: "rust", go: "go",
  js: "javascript", jsx: "jsx", ts: "typescript", tsx: "tsx",
  sh: "bash", lua: "lua", md: "markdown", json: "json",
};

function CodeBlock({ code, language }: { code: string; language: string }) {
  const lang = LANG[language] || "text";
  return (
    <div className="code-block-wrap">
      <span className="code-block-lang">{language}</span>
      <SyntaxHighlighter
        language={lang}
        style={oneDark}
        showLineNumbers
        customStyle={{ margin: 0, borderRadius: 4, maxHeight: 500, fontSize: 13 }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

function NotebookPreview({ raw }: { raw: string }) {
  const { ready, loading: pyLoading, runCode } = usePyodide();
  const [runState, setRunState] = useState<Record<number, string>>({});

  let cells: { type: string; source: string }[] = [];
  try {
    const nb = JSON.parse(raw);
    cells = (Array.isArray(nb.cells) ? nb.cells : [])
      .map((c: { cell_type: string; source: string | string[] }) => ({
        type: c.cell_type,
        source: Array.isArray(c.source) ? c.source.join("") : String(c.source ?? ""),
      }))
      .filter((c: { source: string }) => c.source.trim());
  } catch {
    cells = [{ type: "code", source: raw }];
  }

  async function executeCell(index: number, code: string) {
    setRunState((s) => ({ ...s, [index]: "running" }));
    const output = await runCode(code);
    setRunState((s) => ({ ...s, [index]: output }));
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
              {isCode && ready ? (
                <button
                  type="button"
                  className="notebook-run-btn"
                  onClick={() => executeCell(i, cell.source)}
                  disabled={output === "running"}
                >
                  {output === "running" ? "..." : "▶ Run"}
                </button>
              ) : null}
            </div>
            <SyntaxHighlighter
              language="python"
              style={oneDark}
              customStyle={{ margin: 0, borderRadius: isCode ? 0 : "0 0 4px 4px", fontSize: 13 }}
            >
              {cell.source}
            </SyntaxHighlighter>
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
