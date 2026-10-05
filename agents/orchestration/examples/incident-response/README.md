# 同一份工作流，六种写法：incident-response 示例

场景（贴近 cloud-agent 设计的真实形态）：每天早上 8 点，从 Postgres 的每日事件视图取数据 → 通过 sandbox-broker 拉起一个隔离执行环境（容器/microVM/VM 由 `tier` 声明）→ agent 分两个 prompt 处理（初判级别 → 起草建议）→ 人工审批 → 发布并回收沙箱。

这个目录把**同一份工作流**写成六种格式，用来回答两个问题：

1. "共同分母"里的每个元素（triggers / steps+needs / typed output / retries / approval / 表达式）在真实语法里分别长什么样；
2. "语法开放、语义私有"到底私在哪里——同样的词（retry、approval、output），换个引擎就是另一套行为。

## 文件清单

| 文件 | 谁执行它 | 说明 |
|---|---|---|
| `workflow.json` / `workflow.yml` | 我们的 mini 引擎（`scripts/workflow_dsl_demo.py --file`） | 共同分母语义：step 只有 sql / provision / agent / approval / notify 五种类型 |
| `kestra.yaml` | Kestra（Apache-2.0 引擎+UI，自托管） | 每个 step 都翻译成 Kestra 插件任务；审批 = Pause 任务 |
| `windmill.flow.yaml` | Windmill（OpenFlow schema，AGPL） | 每个 step 都是 rawscript 模块；审批 = 原生 approval 模块 |
| `argo.yaml` | Argo Workflows（k8s CRD） | 每个 step 是一个 container template；审批 = suspend |
| `github-actions.yml` | GitHub Actions | 用来对照"缺什么"：无步骤级重试、无暂停恢复、审批靠 environment 保护规则 |

> 五份外来语法都是**教学示意**（插件类型 id 以各自官方文档为准，做了精简），但对齐全都可以真实执行——差异在语义，不在骨架。

## 共同分母：逐元素对照

| 共同分母元素 | 我们（workflow.json） | Kestra | Windmill OpenFlow | Argo | GitHub Actions |
|---|---|---|---|---|---|
| 触发 | `triggers: [{type: cron, cron}]` | `triggers: [Schedule]` | UI/CLI 里挂 schedule（cron 另配） | 另建 `CronWorkflow` | `on: schedule: [{cron}]`（UTC） |
| 步骤 | `steps: [{id, type}]` | `tasks: [{id, type: 插件}]` | `value.modules: [{type, ...}]` | `templates` + dag tasks | `steps: [{name, run}]` |
| DAG 依赖 | `needs: [a, b]` | 默认顺序执行；DAG 用 `io.kestra.plugin.core.flow.Dag` 包裹 | modules 默认顺序；并行用 `branchall`/forloop | `depends: a && b`（表达式！） | `jobs.<id>.needs`（只能 job 级） |
| 类型化输出 | `output: {type, schema}`（JSON Schema） | 无 schema 声明；输出是插件返回的 KV | `schema`（flow 输入）；步骤结果弱类型 | `outputs.parameters/artifacts`（需声明） | `outputs:`（无类型） |
| 表达式 | `${{ steps.X.output }}` | Pebble `{{ outputs.x.y }}` | `results.x` / `flow_input.x` | `{{tasks.x.outputs.result}}` | `${{ steps.x.outputs.y }}` |
| 重试 | `defaults.retries: {max_attempts, backoff, interval}` | 任务级 `retry: {maxAttempts, interval: PT30S, type: exponential}` | 模块级 `retry: {attempts, interval: 30, exponential: true}` | `retryStrategy: {limit: 3, backoff: {duration: 30s, factor: 2}}` | **没有步骤级重试** |
| 审批门 | `type: approval`（一等步骤） | `type: io.kestra.plugin.core.flow.Pause` | `type: approval` 模块 | `suspend: {}` 模板 | `environment:` 保护规则（job 级） |
| 回收资源 | `teardown: [provision-env]` 步骤字段 | 再写一个任务（顺序靠后） | 再写一个模块 | dag 里再加 task | 再加 step |

## "语义私有"到底私在哪：四个典型

**① retry 是同义词，不是同一物。** 我们的 `max_attempts=3, interval=30s` 翻译过去：Kestra 要写 ISO-8601 时长 + `type: exponential`；Windmill 是秒数 + 布尔开关；Argo 是 `factor` 乘数（隐含指数）且能按表达式挑选失败条件重试；GitHub Actions 干脆没有，你只能自己包一层 `retry` 循环脚本。四份配置**互不可执行**，但表达的是同一个意图——这就是"语法开放（都是 YAML）、语义私有（各引擎自己解释）"。

**② approval 的恢复机制完全不同。** 我们：运行停在 approval 步骤，决策写入账本后继续。Kestra `Pause`：整个 flow 处于 paused，人去 UI 点 resume。Windmill approval：流程挂起，审批页批准后以审批值作为模块输出继续。Argo `suspend`：workflow 冻结，外部 `argo resume`（可带参数）。GitHub Actions：没有流程内暂停——`environment` 保护规则是在 job 开始前卡人，不是步骤间。换言之，"审批"在各家眼里分别是：一等步骤 / 特殊任务 / 特殊模块 / 流程冻结 / 部署门禁。

**③ "起一个沙箱"没有对应物。** 我们的 `type: provision` 背后是 cloud-agent broker 的 E2B 形 API（`tier` 声明隔离档位、TTL、出站白名单）。其他引擎里你只能自己拼：Kestra 是 `http.Request` 或 docker 插件（Kestra 自己起容器，与 broker 无关）；Argo 是起一个 curl 容器；GH Actions 是 `run: curl ...`。**编排层不会替你懂"沙箱"**，这正是 cloud-agent 要把这层语义放进 broker、而不是指望某个工作流引擎的原因。

**④ SQL 步骤的类型化假象。** 我们的 `output: {type: array, items: object}` 是契约；Kestra 的 Query 任务输出什么样由 JDBC 结果集决定（你靠 `{{ outputs.fetch-view.rows }}` 摸索）；Argo 根本没有 SQL 概念，你自己往容器里塞 `psql`；输出"类型"在运行前无人校验。JSON Schema 声明是少数派（我们、Oracle Agent Spec、MS Agent Framework YAML）。

## 跑起来

```bash
# 用我们的 mini 引擎真实执行（toy 步骤处理器，语义见脚本内 handlers）
python ~/projects/benches/agents/orchestration/scripts/workflow_dsl_demo.py \
    --file ~/projects/benches/agents/orchestration/examples/incident-response/workflow.json \
    --auto-approve --workdir /tmp/incident-demo
# 内置同名文档
python ~/projects/benches/agents/orchestration/scripts/workflow_dsl_demo.py \
    --workflow incident-response --auto-approve
```

执行后看 `--workdir/runs/*.json` 的运行账本：每个步骤的开始/完成事件、approval 决策、最终状态——任何引擎都必须提供的最小持久化面。

## 怎么选（对应 cloud-agent §11 的结论）

- 想要"我定义的语义"（provision=broker、approval=账本恢复、agent=RPC 派发）：自研 workflows.yml 只依赖共同分母，翻译到任何引擎都只是"导出"，不是"迁移"。
- 想要现成 UI + 审批 + 大量集成、且接受各家语义：Kestra（Apache-2.0）或 Windmill（AGPL），把 broker/agent 调用写成普通 HTTP 步骤。
- 工作流要挂起数小时-数天、跨 worker、审计级历史：Temporal（workflow-as-code，没有 YAML）。
