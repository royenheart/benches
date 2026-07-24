# Agent 安全 教学专题

系统学习 Agent 安全威胁与防御：从 OWASP Top 10 for LLM Applications 2025 映射到具体攻击向量，从 Prompt Injection 到 Guardrails 和沙箱隔离。

## 目标

1. 掌握 OWASP 2025 Top 10，特别是 5 个 Agent 关键风险（LLM01/05/06/07/08）。
2. 动手复现 direct 和 indirect prompt injection 攻击。
3. 实现 layered defense：input guardrails、tool-call validation、output guardrails、sandboxing。
4. 建立「Prompt 指令不是安全边界」的安全思维。

## 目录结构

```text
agents/safety/
├── README.md
├── notebooks/
│   ├── 00_threat_modeling_owasp.ipynb
│   ├── 01_prompt_injection.ipynb
│   └── 02_guardrails_and_sandboxing.ipynb
└── scripts/
    ├── threat_model_demo.py
    └── guardrail_demo.py
```

## 快速开始

```bash
python agents/safety/scripts/threat_model_demo.py --agent-config basic --attack prompt-injection
python agents/safety/scripts/guardrail_demo.py --pipeline full --strictness high
# API mode — 真实注入攻防
python agents/safety/scripts/guardrail_demo.py --use-api
python agents/safety/scripts/threat_model_demo.py --agent-config privileged --attack excessive-agency --use-api
jupyter notebook agents/safety/notebooks
```

## Notebook 顺序

### 00. 威胁建模与 OWASP Top 10

- OWASP Top 10 for LLM Applications 2025 逐一解读。
- 以「文件管理 Agent」为例，标注每个 OWASP 风险的攻击面。
- 风险评估矩阵：Likelihood × Impact → Severity。
- 练习：给你设计的 Agent 做威胁建模。

### 01. Prompt Injection 攻防

- Direct injection：用户输入劫持 Agent 行为。
- Indirect injection：工具返回内容（网页、邮件、文档）中包含恶意指令。
- 防御：instruction delimiters、输入净化、敏感指令隔离。
- 练习：绕过简单的 prompt injection 防御。

### 02. Guardrails 与沙箱

- Guardrails 层次：input filter → tool-call allow-list → output validator。
- 沙箱：限制工具权限（只读 vs 读写）、资源配额、网络隔离。
- Least privilege 原则：Agent 只拥有完成任务所需的最小权限。
- Confirmation gates：不可逆操作需要人工确认。

## 可调参数

- `threat_model_demo.py`
  - `--agent-config`：basic / privileged / multi-tool
  - `--attack`：prompt-injection / tool-poisoning / excessive-agency

- `guardrail_demo.py`
  - `--pipeline`：input / output / full
  - `--strictness`：low / medium / high

## 资料入口

- OWASP GenAI Security (2025): [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/)
- NVIDIA NeMo Guardrails: [github.com/NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails)
- Guardrails AI: [github.com/guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails)
- OWASP 2023 v1.1: [owasp.org/www-project-top-10-for-large-language-model-applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
