import { chromium } from "playwright-core";

const url = process.env.BENCHES_BOARD_URL ?? "http://localhost:5173";
const executablePath = process.env.CHROME_BIN ?? "/usr/bin/google-chrome";
const screenshotPath = process.env.BENCHES_BOARD_SCREENSHOT ?? "/tmp/benches-board-verify.png";

const browser = await chromium.launch({
  executablePath,
  headless: true,
  args: ["--no-sandbox"]
});

try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1
  });
  const logs = [];
  page.on("console", (message) => logs.push({ type: message.type(), text: message.text() }));
  page.on("pageerror", (error) => logs.push({ type: "pageerror", text: error.message }));

  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForFunction(() => {
    const board = document.querySelector('[data-testid="cytoscape-board"]');
    const cy = board?._cyreg?.cy;
    return Boolean(cy && cy.nodes().length > 0);
  });
  await page.waitForTimeout(800);
  const initialPositions = await page.evaluate(() => {
    const cy = document.querySelector('[data-testid="cytoscape-board"]')?._cyreg?.cy;
    return Object.fromEntries(cy.nodes().map((node) => [node.id(), node.position()]));
  });
  await page.evaluate(() => {
    document.querySelector('[data-testid="cytoscape-board"]')?._cyreg?.cy?.$id("minimum-window").emit("tap");
  });
  await waitForFocusedTopic(page, "minimum-window");

  const state = await page.evaluate(() => {
    const board = document.querySelector('[data-testid="cytoscape-board"]');
    const cy = board?._cyreg?.cy;
    if (!cy) {
      return { ok: false, reason: "missing cytoscape instance" };
    }

    const nodes = cy.nodes().map((node) => {
      const box = node.renderedBoundingBox();
      return {
        id: node.id(),
        visible: node.visible(),
        focused: Boolean(node.data("focused")),
        renderedPosition: node.renderedPosition(),
        position: node.position(),
        box,
        finite:
          Number.isFinite(node.position("x")) &&
          Number.isFinite(node.position("y")) &&
          Number.isFinite(box.x1) &&
          Number.isFinite(box.y1) &&
          Number.isFinite(box.w) &&
          Number.isFinite(box.h),
        onScreen:
          box.x2 > 0 &&
          box.y2 > 74 &&
          box.x1 < window.innerWidth &&
          box.y1 < window.innerHeight &&
          box.w > 20 &&
          box.h > 20
      };
    });
    const overlaps = [];
    for (let leftIndex = 0; leftIndex < nodes.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < nodes.length; rightIndex += 1) {
        const left = nodes[leftIndex];
        const right = nodes[rightIndex];
        if (
          left.box.x1 < right.box.x2 &&
          left.box.x2 > right.box.x1 &&
          left.box.y1 < right.box.y2 &&
          left.box.y2 > right.box.y1
        ) {
          overlaps.push({
            left: left.id,
            right: right.id,
            leftBox: left.box,
            rightBox: right.box
          });
        }
      }
    }

    const currentPositions = Object.fromEntries(cy.nodes().map((node) => [node.id(), node.position()]));
    const highlightedEdges = cy.edges().map((edge) => ({
      id: edge.id(),
      highlighted: Boolean(edge.data("highlighted"))
    }));

    return {
      ok:
        nodes.length > 0 &&
        nodes.every((node) => node.visible && node.finite && node.onScreen) &&
        overlaps.length === 0,
      nodeCount: nodes.length,
      edgeCount: cy.edges().length,
      size: { width: cy.width(), height: cy.height() },
      zoom: cy.zoom(),
      pan: cy.pan(),
      overlaps,
      currentPositions,
      highlightedEdges,
      nodes
    };
  });
  const movedNodes = Object.entries(initialPositions).filter(([nodeId, initialPosition]) => {
    const currentPosition = state.currentPositions[nodeId];
    if (!currentPosition) {
      return true;
    }
    return (
      Math.abs(currentPosition.x - initialPosition.x) > 1 ||
      Math.abs(currentPosition.y - initialPosition.y) > 1
    );
  });
  state.positionStableAfterClick = movedNodes.length === 0;
  state.movedNodes = movedNodes.map(([nodeId]) => nodeId);
  state.minimumWindowFocused = state.nodes.some((node) => node.id === "minimum-window" && node.focused);
  state.ok = state.ok && state.positionStableAfterClick && state.minimumWindowFocused;

  await page.screenshot({ path: screenshotPath, fullPage: true });

  const badLogs = logs.filter(
    (log) =>
      log.type === "pageerror" ||
      (log.type === "error" && !log.text.includes("Failed to load resource"))
  );
  console.log(JSON.stringify({ state, badLogs, screenshotPath }, null, 2));

  if (!state.ok || badLogs.length) {
    process.exitCode = 1;
  }
} finally {
  await browser.close();
}

async function waitForFocusedTopic(page, topicId) {
  await page.waitForFunction((expectedTopicId) => {
    const board = document.querySelector('[data-testid="cytoscape-board"]');
    const cy = board?._cyreg?.cy;
    if (!cy || cy.nodes().length === 0) {
      return false;
    }

    const focused = cy.nodes().toArray().find((node) => node.data("focused"));
    if (!focused) {
      return false;
    }

    return focused.id() === expectedTopicId;
  }, topicId);
}
