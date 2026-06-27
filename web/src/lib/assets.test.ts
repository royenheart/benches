import { describe, expect, it } from "vitest";
import { assetMatchesQuery, classifyAsset } from "./assets";

describe("asset helpers", () => {
  it("classifies repository assets by path and extension", () => {
    expect(classifyAsset("algorithms/competitive/sliding_window.md")).toMatchObject({
      name: "sliding_window.md",
      ext: ".md",
      type: "markdown",
      domain: "algorithms",
      previewable: true
    });
    expect(classifyAsset("accels/triton/notebooks/00_setup.ipynb")).toMatchObject({
      type: "notebook",
      domain: "accels",
      previewable: true
    });
    expect(classifyAsset("accels/problems/demo/answer.cu")).toMatchObject({
      type: "source",
      previewable: true
    });
    expect(classifyAsset("accels/problems/demo/handout.pdf")).toMatchObject({
      type: "pdf",
      previewable: false
    });
  });

  it("matches assets by name, path, type, and domain", () => {
    const asset = classifyAsset("algorithms/competitive/leetcode_239_sliding_window_max.cpp");

    expect(assetMatchesQuery(asset, "239")).toBe(true);
    expect(assetMatchesQuery(asset, "competitive")).toBe(true);
    expect(assetMatchesQuery(asset, "source")).toBe(true);
    expect(assetMatchesQuery(asset, "numerics")).toBe(false);
  });
});
