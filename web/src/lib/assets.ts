import type { Asset, AssetType } from "../types";

const sourceExts = new Set([
  ".c",
  ".cc",
  ".cpp",
  ".cu",
  ".cuh",
  ".h",
  ".hpp",
  ".py",
  ".rs",
  ".go",
  ".js",
  ".jsx",
  ".ts",
  ".tsx",
  ".sh",
  ".lua"
]);

const dataExts = new Set([".json", ".csv", ".txt", ".data", ".dat", ".npy", ".npz"]);

export function classifyAsset(path: string): Asset {
  const normalized = path.replaceAll("\\", "/");
  const parts = normalized.split("/");
  const name = parts.at(-1) ?? normalized;
  const domain = parts[0] || "root";
  const extMatch = name.match(/\.[^.]+$/);
  const ext = extMatch ? extMatch[0].toLowerCase() : "";
  const type = classifyType(ext);

  return {
    path: normalized,
    name,
    ext,
    type,
    domain,
    previewable: type === "markdown" || type === "notebook" || type === "source" || type === "data"
  };
}

export function assetMatchesQuery(asset: Asset, query: string): boolean {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  return [asset.path, asset.name, asset.ext, asset.type, asset.domain]
    .filter(Boolean)
    .some((field) => field.toLowerCase().includes(normalized));
}

function classifyType(ext: string): AssetType {
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
