# Agent Skills 与 Harness 设计 教学专题

2025 年底以来的工程范式转移：能力不再全部写进 system prompt，而是做成 **Skills**（按需加载的指令包）；Agent 的本体退化为一个通用 **Harness**（循环 + 工具 + 调度）。本专题解剖这个范式并动手实现。

## 目标

1. 理解 Progressive Disclosure 三层加载：metadata（常驻）→ instructions（触发时）→ resources（用到时）。
2. 解剖 Claude Code 式 harness：system prompt、tools、subagents、hooks、slash commands、权限模型。
3. 动手实现 mini skill loader + mini harness，用真实 LLM 验证 skill 注入前后的行为差异。

## 目录结构

```text
agents/agent-skills/
├── README.md
├── notebooks/
│   ├── 00_progressive_disclosure.ipynb
│   ├── 01_harness_design.ipynb
│   └── 02_build_a_skill_system.ipynb
├── scripts/
│   ├── skill_loader_demo.py
│   └── mini_harness_demo.py
└── skills/                    # 示例 skill（供 loader 扫描）
    └── unit-converter/
        └── SKILL.md
```

## 快速开始

```bash
# Toy mode — 关键词匹配 + 模板回答
python agents/agent-skills/scripts/skill_loader_demo.py --query "把 5 公里换算成英里" --verbose
python agents/agent-skills/scripts/mini_harness_demo.py --scenario review --verbose

# API mode — LLM 选择 skill + 注入后真实回答
python agents/agent-skills/scripts/skill_loader_demo.py --query "把 5 公里换算成英里" --use-api --verbose
python agents/agent-skills/scripts/mini_harness_demo.py --scenario review --use-api --verbose
jupyter notebook agents/agent-skills/notebooks
```

## Notebook 顺序

### 00. Progressive Disclosure

- 三层加载解剖：扫描时只读 frontmatter（name + description，约 100 token）；触发时才读正文；正文引用的资源文件用到才读。
- 以本仓库 `.agents/skills/` 为活教材：统计每个 skill 的 metadata 与正文 token 量。
- 为什么这是唯一可扩展的方案：100 个 skill 全量注入 = 100K token；三层加载常驻成本 ≈ 10K。

### 01. Harness 设计解剖

- Claude Code 式 harness 的组件：主循环、工具集、subagent 委派、Pre/PostToolUse hooks、slash commands、权限规则。
- Hook 的本质：在工具调用前后插入确定性检查（不经过 LLM）— 安全规则的可靠落点。
- Subagent 的价值：隔离 context（探索性任务的中间噪声不进主 context）。

### 02. 动手：自建 Skill 系统

- 实现 skill loader：扫描 SKILL.md → 解析 frontmatter → LLM 选择 → 注入正文。
- 实验：同一问题，无 skill vs 注入 skill 的回答质量对比（真实 API）。
- 设计自己的 skill：为一个你熟悉的领域写 SKILL.md，验证触发率。

## 可调参数

- `skill_loader_demo.py`
  - `--query`：用户问题
  - `--skills-dir`：skill 扫描目录（默认 `agents/agent-skills/skills`）
  - `--use-api`：LLM 选择 skill + 真实回答

- `mini_harness_demo.py`
  - `--scenario`：review / explore
  - `--use-api`：LLM 驱动主循环与 subagent
  - `--verbose`：打印 hook 拦截与 subagent 委派 trace

## 资料入口

- Anthropic Agent Skills: [anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Claude Code Subagents: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
- Claude Code Hooks: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- 本仓库活教材：`../../.agents/skills/benches-development/SKILL.md`
