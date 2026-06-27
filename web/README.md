# Benches Topics Board

This is the web knowledge board for the `benches` repository.

## Local Dynamic Mode

Use this mode while editing topics on the remote development machine:

```bash
cd web
npm install
npm run dev:local
```

The server binds to `0.0.0.0` and prints a URL such as `http://localhost:5173`. In a remote VSCode session, forward that port from the Ports panel and open the forwarded local URL.

Local mode provides:

- topic board browsing;
- read/edit mode switch;
- right-click blank board space in edit mode to create topics;
- double-click topic in edit mode to edit;
- repository asset scanning through `/api/assets`;
- topic persistence through `/api/topics`;
- static export through `/api/export`.

## Static Read-Only Mode

Static deployment reads `public/data/topics.json` and `public/data/assets.json`.

```bash
cd web
npm run build
```

Deploy `web/dist/` to GitHub Pages or any static server. Static mode has no write API, so editing and saving are unavailable outside local dynamic mode.

## Data Files

- `public/data/topics.json`: board topics and topic relationships used by static builds.
- `public/data/assets.json`: exported repository asset index.
- `content/topics.json`: optional local write target created by the dynamic API after saving.

The UI is the intended editing surface. The JSON files are implementation details for persistence and static deployment.
