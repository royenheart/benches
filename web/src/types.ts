export type AssetType = "markdown" | "notebook" | "source" | "pdf" | "data" | "other";

export type TopicKind =
  | "problem"
  | "collection"
  | "paradigm"
  | "interview"
  | "puzzle"
  | "note"
  | "custom";

export type EdgeKind =
  | "related"
  | "prerequisite"
  | "variant"
  | "same-pattern"
  | "custom";

export interface Asset {
  path: string;
  name: string;
  ext: string;
  type: AssetType;
  domain: string;
  previewable: boolean;
}

export interface TopicAssetRef {
  path: string;
  label?: string;
  position?: { x: number; y: number };
}

export interface Topic {
  id: string;
  title: string;
  summary: string;
  kind: TopicKind;
  tags: string[];
  position: { x: number; y: number };
  size: { width: number; height: number };
  theme?: { color?: string; cover?: string };
  body: string;
  assetRefs: TopicAssetRef[];
}

export interface TopicEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  kind: EdgeKind;
}

export interface BoardData {
  topics: Topic[];
  edges: TopicEdge[];
}

export type BoardMode = "read" | "edit";
