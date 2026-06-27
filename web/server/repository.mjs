import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const ignoredDirs = new Set([
  ".git",
  ".superpowers",
  ".xmake",
  ".venv",
  "web",
  "node_modules",
  "dist",
  "build",
  "builds",
  "backups",
  "__pycache__",
  ".pytest_cache"
]);

const includedExts = new Set([
  ".md",
  ".markdown",
  ".ipynb",
  ".cpp",
  ".cc",
  ".c",
  ".cu",
  ".cuh",
  ".h",
  ".hpp",
  ".py",
  ".sh",
  ".lua",
  ".pdf",
  ".json",
  ".csv",
  ".txt",
  ".data",
  ".dat"
]);

const sourceExts = new Set([
  ".c",
  ".cc",
  ".cpp",
  ".cu",
  ".cuh",
  ".h",
  ".hpp",
  ".py",
  ".sh",
  ".lua"
]);

const dataExts = new Set([".json", ".csv", ".txt", ".data", ".dat"]);

export async function scanAssets(rootDir) {
  const root = path.resolve(rootDir);
  const assets = [];

  async function walk(currentDir) {
    const entries = await readdir(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.name.startsWith(".")) {
        continue;
      }

      const absolute = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        if (!ignoredDirs.has(entry.name)) {
          await walk(absolute);
        }
        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      const ext = path.extname(entry.name).toLowerCase();
      if (!includedExts.has(ext)) {
        continue;
      }

      assets.push(classifyAsset(path.relative(root, absolute).split(path.sep).join("/")));
    }
  }

  await walk(root);
  return assets.sort((left, right) => left.path.localeCompare(right.path));
}

export async function readAssetPreview(rootDir, relativePath) {
  const absolute = safeResolve(rootDir, relativePath);
  const ext = path.extname(absolute).toLowerCase();

  if (ext === ".pdf") {
    return "PDF 文件可被引用；静态预览暂不展开正文。";
  }

  const text = await readFile(absolute, "utf8");
  if (ext === ".ipynb") {
    return notebookPreview(text);
  }

  return text.slice(0, 5000);
}

function classifyAsset(relativePath) {
  const parts = relativePath.split("/");
  const name = parts.at(-1) ?? relativePath;
  const ext = path.extname(name).toLowerCase();
  const type = classifyType(ext);

  return {
    path: relativePath,
    name,
    ext,
    type,
    domain: parts[0] || "root",
    previewable: type === "markdown" || type === "notebook" || type === "source" || type === "data"
  };
}

function classifyType(ext) {
  if (ext === ".md" || ext === ".markdown") {
    return "markdown";
  }
  if (ext === ".ipynb") {
    return "notebook";
  }
  if (sourceExts.has(ext)) {
    return "source";
  }
  if (ext === ".pdf") {
    return "pdf";
  }
  if (dataExts.has(ext)) {
    return "data";
  }
  return "other";
}

function notebookPreview(text) {
  const notebook = JSON.parse(text);
  const cells = Array.isArray(notebook.cells) ? notebook.cells : [];
  return cells
    .slice(0, 8)
    .map((cell) => {
      const source = Array.isArray(cell.source) ? cell.source.join("") : String(cell.source ?? "");
      return `[${cell.cell_type ?? "cell"}]\n${source}`;
    })
    .join("\n\n")
    .slice(0, 5000);
}

function safeResolve(rootDir, relativePath) {
  const root = path.resolve(rootDir);
  const absolute = path.resolve(root, relativePath);

  if (absolute !== root && !absolute.startsWith(`${root}${path.sep}`)) {
    throw new Error("Asset path escapes repository root");
  }

  return absolute;
}
