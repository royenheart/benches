import { mkdir, readFile, writeFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createServer as createViteServer } from "vite";
import { readAssetPreview, scanAssets } from "./repository.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(webRoot, "..");
const contentDir = path.join(webRoot, "content");
const publicDataDir = path.join(webRoot, "public", "data");
const contentTopicsPath = path.join(contentDir, "topics.json");
const publicTopicsPath = path.join(publicDataDir, "topics.json");
const publicAssetsPath = path.join(publicDataDir, "assets.json");
const port = Number(process.env.PORT ?? 5173);

const vite = await createViteServer({
  root: webRoot,
  server: { middlewareMode: true },
  appType: "spa"
});

const server = http.createServer(async (req, res) => {
  try {
    if (await handleApi(req, res)) {
      return;
    }
  } catch (error) {
    sendJson(res, 500, { error: error instanceof Error ? error.message : String(error) });
    return;
  }

  vite.middlewares(req, res, () => {
    res.statusCode = 404;
    res.end("Not found");
  });
});

server.listen(port, "0.0.0.0", () => {
  console.log(`Benches topics board: http://localhost:${port}`);
});

async function handleApi(req, res) {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "GET" && url.pathname === "/api/topics") {
    sendJson(res, 200, await readTopics());
    return true;
  }

  if (req.method === "PUT" && url.pathname === "/api/topics") {
    const topics = await readJsonBody(req);
    await writeTopics(topics);
    sendJson(res, 200, { ok: true });
    return true;
  }

  if (req.method === "GET" && url.pathname === "/api/assets") {
    sendJson(res, 200, await scanAssets(repoRoot));
    return true;
  }

  if (req.method === "GET" && url.pathname === "/api/assets/preview") {
    const assetPath = url.searchParams.get("path");
    if (!assetPath) {
      sendJson(res, 400, { error: "Missing path query parameter" });
      return true;
    }
    sendJson(res, 200, { path: assetPath, preview: await readAssetPreview(repoRoot, assetPath) });
    return true;
  }

  if (req.method === "POST" && url.pathname === "/api/export") {
    const topics = await readTopics();
    const assets = await scanAssets(repoRoot);
    await mkdir(publicDataDir, { recursive: true });
    await writeFile(publicTopicsPath, `${JSON.stringify(topics, null, 2)}\n`);
    await writeFile(publicAssetsPath, `${JSON.stringify(assets, null, 2)}\n`);
    sendJson(res, 200, { ok: true, topics: topics.topics.length, assets: assets.length });
    return true;
  }

  return false;
}

async function readTopics() {
  try {
    return JSON.parse(await readFile(contentTopicsPath, "utf8"));
  } catch {
    return JSON.parse(await readFile(publicTopicsPath, "utf8"));
  }
}

async function writeTopics(topics) {
  if (!Array.isArray(topics?.topics) || !Array.isArray(topics?.edges)) {
    throw new Error("Invalid topics payload");
  }

  await mkdir(contentDir, { recursive: true });
  await mkdir(publicDataDir, { recursive: true });
  const text = `${JSON.stringify(topics, null, 2)}\n`;
  await writeFile(contentTopicsPath, text);
  await writeFile(publicTopicsPath, text);
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function sendJson(res, status, payload) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.end(`${JSON.stringify(payload, null, 2)}\n`);
}
