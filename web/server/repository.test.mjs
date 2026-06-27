import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { readAssetPreview, scanAssets } from "./repository.mjs";

describe("repository asset scanning", () => {
  it("scans previewable repository assets and skips ignored working directories", async () => {
    const root = await mkdtemp(path.join(tmpdir(), "benches-assets-"));
    await mkdir(path.join(root, "algorithms", "competitive"), { recursive: true });
    await mkdir(path.join(root, ".agents", "skills"), { recursive: true });
    await mkdir(path.join(root, "web", "node_modules", "pkg"), { recursive: true });
    await mkdir(path.join(root, "backups", "old"), { recursive: true });
    await writeFile(path.join(root, "algorithms", "competitive", "answer.cpp"), "int main() {}");
    await writeFile(path.join(root, ".agents", "skills", "ignored.md"), "# ignored");
    await writeFile(path.join(root, "web", "node_modules", "pkg", "ignored.md"), "# ignored");
    await writeFile(path.join(root, "backups", "old", "ignored.md"), "# ignored");

    const assets = await scanAssets(root);

    expect(assets.map((asset) => asset.path)).toEqual([
      "algorithms/competitive/answer.cpp"
    ]);
    expect(assets[0]).toMatchObject({
      type: "source",
      domain: "algorithms",
      previewable: true
    });
  });

  it("returns compact text previews for markdown and notebook files", async () => {
    const root = await mkdtemp(path.join(tmpdir(), "benches-preview-"));
    await mkdir(path.join(root, "notes"), { recursive: true });
    await writeFile(path.join(root, "notes", "topic.md"), "# Title\n\nBody text");
    await writeFile(
      path.join(root, "notes", "topic.ipynb"),
      JSON.stringify({
        cells: [
          { cell_type: "markdown", source: ["# Notebook\n", "Intro"] },
          { cell_type: "code", source: ["print(1)"] }
        ]
      })
    );

    await expect(readAssetPreview(root, "notes/topic.md")).resolves.toContain("Body text");
    await expect(readAssetPreview(root, "notes/topic.ipynb")).resolves.toContain("Notebook");
  });
});
