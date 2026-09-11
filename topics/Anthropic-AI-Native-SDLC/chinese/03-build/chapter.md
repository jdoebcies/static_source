# 03 Build：开发实现

没有获准的计划，就不开始实现。组织知识成为 Agent 能够读取的文件，保护措施以代码运行，而不只依赖工作习惯。

## 默认从 Claude Code 计划模式开始

工程师以[计划模式](https://code.claude.com/docs/en/permission-modes)启动 Claude Code 会话，把第 2 阶段“设计”中获准的 `spec.md` 交给 Claude，让它向自己提问，持续调整计划，直到工程师满意。

**传统方式。** 工程师读完设计便开始写代码。怎样实现改动、具体修改哪些文件、需要哪些测试，这些信息留在工程师脑中，最多写在工单评论里，其他人无法提前评审。评审者首次看到的就是已经完成的 diff，此时返工已经很慢。

**AI 原生方式。** 工作从书面计划开始。Claude 在计划模式中读取代码库，但不做改动，据此生成计划。工程师在写代码前纠正计划，批准后的版本提交为 `plan.md`，供后续阶段对照检查。

### 如何开始

**前置条件：** 如果已经有意图交付物，就提供 `intent.md` 或 `spec.md`；有 `CLAUDE.md` 也会有所帮助。

**基础设施：** 能够访问仓库的 Claude Code。

### 如何执行

1. 工程师在计划模式下启动与 Claude 的会话。
2. 提供 `intent.md` 与 `spec.md`，要求实施计划列明要修改的文件、工作顺序，以及证明改动的测试。
3. 追问计划：这次改动可能破坏什么？哪一步风险最高？Claude 考虑后放弃了哪些其他方案？
4. 持续修改，直到一个没看过这段对话的工程师，也能仅凭计划实施改动。
5. 将批准后的计划提交为 `plan.md`，纳入审计轨迹。第 5 阶段“部署”中的 PR 评审将对照它检查最终 diff。
6. 接受计划，让 Claude 实现。计划足够扎实时，实现往往一轮即可完成。
7. 实现偏离计划时，在同一次提交中更新 `plan.md`。可以考虑用 Hook 强制两者同步。

### plan.md 示例

```markdown
# Plan: claims status self-service (from intent.md 2026-06-02)

## Files that change
portal/src/claims/StatusPanel.tsx (new), claims-api/routes/status.py,
claims-api/tests/test_status.py

## Order of work
1. Add the status endpoint behind existing auth.
2. Panel against the endpoint.
3. Wire into the portal nav.

## Risks
The claims-core API rate-limits at 50 rps; the panel must cache.

## Proof
test_status.py covers the four claim states; screenshot matches the
approved mock.
```

**示例中的文字。** 计划是理赔状态自助查询，来源为 2026-06-02 的意图文件。新增 `StatusPanel.tsx`，修改状态路由和对应测试。顺序是先在既有认证后增加状态接口，再实现对接接口的面板，最后接入门户导航。风险是 `claims-core API` 每秒限流 50 次请求，因此面板必须缓存。验证要求为 `test_status.py` 覆盖四种理赔状态，截图符合已经批准的设计稿。

### 治理方面的考虑

设计评审在生成任何代码之前进行。此时调整方向，仍然只需修改文档。计划模式本身就执行这项限制：工程师接受计划前，Claude 无法编辑文件。计划及其修订与接受者身份一起留档。日常改动由工程师批准，组织认定为较高风险的事项交给技术负责人或架构师。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 第一轮实现后即可合并的改动比例，以及从计划批准到 PR 合并的时间。所需数据来自 PR 元数据。 |
| 滞后指标 | 每次改动的返工轮次，同样从 PR 元数据取得；另检查合并后的 diff 有多经常仍与已提交的 `plan.md` 一致。 |

## Claude Code 自动模式

Claude Code 也可以运行在自动模式中。工程师反复调整并批准计划、确认满意后，Claude 每次应用改动时无需再逐次提示确认。随着后文各项方法中的保护措施成熟，包括调整好的 `CLAUDE.md`、表达政策的 Skills、阻止不安全动作的 Hooks，以及 Claude 能运行的测试套件，自动接受会成为日常工作的默认方式。这类工作应当有清楚的 `spec.md`、较小的影响范围，而且已有测试覆盖相关代码。

人的工作会从观察 Agent 每次编辑、逐项审核动作，转向在较长的自主会话结束后审查交付物。自动接受与 worktree 结合，还能支持个人和团队开展并行工作；它也是第 6 阶段“维护”中自主运行 SDLC、形成循环的基础。

## 侧栏：旧系统与权威记录

本节适用于流程产生的每一项交付物。

既有 SDLC 很可能已经在追踪交付物，只是没有放在 Markdown 文件中。工作项可能在 Jira，需求放在内置监管追溯能力的工具里，设计在 Figma，变更批准则由变更委员会记录。这些系统很难被替换，因为审计人员和监管方已经接受它们，其他团队也依赖它们。因此，AI 原生 SDLC 必须能够适配现状。

转向 AI 原生 SDLC 时，要为每种交付物指定一个系统作为权威记录（source of truth），其他地方保存副本或原记录链接。可以采用以下配置，每种交付物的选择可以不同：

- **仓库作为权威记录。** Markdown 交付物是正式记录，旧系统引用某次提交中的文件。对于工程主导的组织，这可能是较简洁的配置：所有记录使用同一工具和同一时间戳权威。
- **旧系统作为权威记录。** Jira、ServiceNow 或需求工具保存正式记录，Markdown 是工作副本。Claude 在会话开始时读取记录，在生成规格或计划的同一会话中，通过 [MCP](https://code.claude.com/docs/en/mcp) 连接器把结果写回。
- **相互关联作为最低要求。** 所有交付物注明记录 ID，所有旧系统记录包含 Markdown 文件的 commit SHA。过渡到 AI 原生 SDLC 时，可以从这种关联方式开始，同时接受目前存在两处权威记录的事实。

旧系统与 Markdown 优先的系统可以共存，前提是两者建立关联，或明确其中一个是权威记录。

## CLAUDE.md

[`CLAUDE.md`](https://code.claude.com/docs/en/memory) 为 Claude 提供新成员入职时需要的上下文，涵盖约定、命令、架构和团队最常见的错误。过去存在人脑和 Wiki 中的知识，变成 Agent 每次会话开始时读取的文件，由整个团队维护，并在出错后持续调整。

### 如何开始

**前置条件：** 无。

**基础设施：** 一个仓库、已安装的 Claude Code，以及一位熟悉代码库的工程师。

### 如何执行

1. 在仓库中运行 `/init`，让 Claude 根据发现的内容生成初始 `CLAUDE.md`。
2. 将文件精简到新成员第一天所需的信息：保留构建、测试和 lint 命令，重要约定，以及 Claude 反复犯错的地方。
3. 在仓库根目录提交 `CLAUDE.md`，让团队共享一个版本，并像代码一样评审修改。
4. 可以采用一条工作规则：Claude 同一种错误犯了两次，就把纠正说明写进 `CLAUDE.md`。
5. 文件控制在一页以内。Claude 在会话开始时会通读整个文件，过时信息只会白占上下文。

### CLAUDE.md 示例

```markdown
# Payments service

## Commands
- Build: make build
- Test: make test (unit), make itest (integration, needs docker)
- Lint: make lint (runs in CI; fix before pushing)

## Conventions
- Java 21, Spring Boot 3. No new Lombok.
- Money is always BigDecimal, never double.
- Every endpoint needs an integration test in src/itest.

## Architecture
- api/ holds REST controllers, core/ holds domain logic,
  adapters/ talks to external systems.
- Kafka events are defined in schemas/; never edit generated classes.

## Things Claude gets wrong
- Do not bump dependency versions; the platform team owns them.
- The legacy v1/ package is frozen; changes go in v2/.
```

**示例中的文字。** 支付服务的命令为 `make build`、单元测试 `make test`、需要 Docker 的集成测试 `make itest`，以及在 CI 中运行的 `make lint`；推送前修复 lint 问题。约定使用 Java 21、Spring Boot 3，不新增 Lombok 用法；金额始终使用 `BigDecimal`，绝不使用 `double`；每个端点在 `src/itest` 中有集成测试。架构中，`api/` 放 REST 控制器，`core/` 放领域逻辑，`adapters/` 连接外部系统；Kafka 事件定义在 `schemas/`，不得编辑生成类。常见错误提示是：依赖版本由平台团队管理，不得自行升级；旧 `v1/` 包已冻结，修改放到 `v2/`。

### 治理方面的考虑

`CLAUDE.md` 纳入版本控制，Agent 遵守的指令就能够评审和审计。文件承载团队约定，修改记录保存在 Git 历史中，由代码所有者在 PR 评审中批准。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | Claude 重复出现本应被 `CLAUDE.md` 纠正的错误的频率。对 `CLAUDE.md` 的修正和变更应在 Git 历史中追踪。 |
| 滞后指标 | 新团队成员从开始工作到首个 PR 合并所需的时间，从 PR 历史获取。 |

## 用 Skills 承载组织知识

Skills 使组织知识能够应用于实际工作：指令明确、纳入版本控制、广泛采用，并在政策改变时集中更新。一个经验原则是：需要一致应用的组织知识适合写成 Skill；本应放在 `CLAUDE.md` 或提示词里的内容，不要另写成 Skill。

### 如何开始

**前置条件：** 没有必需项。`CLAUDE.md` 能把 Agent 的工作知识保存在仓库中，因此有所帮助，但 Skill 并不依赖它。

**基础设施：** 一项有具名负责人、有书面权威记录的政策。

### 如何执行

1. 选择一项目前执行不一致的知识，可以是安全标准、API 设计约定或品牌规则。
2. 将其写为 Skill：一个包含 `SKILL.md` 的目录，frontmatter 说明何时触发，正文说明做什么。工程师依据政策负责人的权威记录起草，可以让 Claude 协助。
3. 将 Skill 放在仓库的 `.claude/skills/<name>/`，与代码一起交付；也可以通过[插件](https://code.claude.com/docs/en/plugin-marketplaces)在组织内分发。
4. 测试触发是否可靠。用不同说法请 Claude 完成相关任务，确认每次都加载 Skill。
5. 政策改变时修改 Skill，并由政策负责人批准。
6. 工程师在下次会话自动使用新版本。

### 示例：.claude/skills/secure-api-review/SKILL.md

```markdown
---
name: secure-api-review
description: Apply the API security standard. Use whenever creating or
  modifying an external-facing endpoint, reviewing API code, or
  generating an OpenAPI spec.
---
# Secure API review

When you create or change an API endpoint:
1. Authentication: every endpoint requires the gateway JWT;
   no anonymous routes outside /health.
2. Input validation: validate request bodies against the OpenAPI
   schema and reject unknown fields.
3. Audit: every state-changing endpoint emits an audit event with
   actor, action, entity and timestamp.
4. Data classification: fields tagged pii in the schema must never
   appear in logs or error messages.

Run scripts/check-endpoints.sh and include its output in your summary.
```

**示例中的文字。** 创建或修改对外端点、评审 API 代码或生成 OpenAPI 规格时，应用 API 安全标准。端点必须使用网关 JWT，`/health` 以外不允许匿名路由；按 OpenAPI schema 校验请求体，拒绝未知字段；所有改变状态的端点都发出审计事件，包含操作人、动作、实体和时间戳；schema 中标为 `pii` 的字段不得出现在日志或错误信息中。运行 `scripts/check-endpoints.sh`，在摘要中附上输出。

### 治理方面的考虑

Skill 是一种控制措施，但它提供的是指导。它让 Claude 更有可能在写代码时应用政策，却没有机制强迫会话遵守。必须始终成立的政策，需要 Skill 背后的确定性机制支持，例如阻止动作的 Hook，或在 PR 中重新检查政策的评审。Skill 让违规变得少见，Hook 让违规接近不可能。Skill 调用记录在会话追踪中，政策负责人像评审代码一样审阅 Skill 修改。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 从政策负责人批准政策变更，到更新后的 Skill 合并所需的时间，从 Skill 目录相关 PR 获取。 |
| 滞后指标 | PR 评审中引用该政策的问题数量。Skill 在编码时开始应用政策后，这类发现应趋近于零。如果这类发现没有趋近于零，要么 Skill 没有触发，要么其文字已经偏离正式政策。 |

## 把 Hooks 用作开发时的保护措施

Skill 提供指导，[Hook](https://code.claude.com/docs/en/hooks) 是背后的确定性执行层。Claude 在实现期间大多是在编辑文件和执行 Shell 命令，因此开发实现阶段可能最频繁地触发 Hooks。

开发阶段的 Hook 可以：

- 阻止编辑生成类、冻结包等受保护路径；
- 每次编辑后运行格式化器和 lint，避免偏差累积；
- 阻止凭据进入 diff。

凡是必须无例外遵守的 Skill 政策，都应有这些机制支持。Hook 会在每次匹配动作发生时运行，因此开发阶段的 Hooks 应当快速，并限定于变更文件。完整测试套件等较重的检查应放在提交或 PR 阶段。

向人请求批准的 Hook 应与第 5 阶段“部署”的审批关口一起安排，因为开发期间的批准提示，会让人重新成为所有并行会话的必经环节。

## 并行会话与子代理

一位工程师可以同时推进几条工作线。

并行会话是另一个完整的 Claude Code 实例，在自己的 [Git worktree](https://code.claude.com/docs/en/worktrees) 中处理独立任务。会话彼此不了解，唯一的共同点是指导它们的工程师。

[子代理](https://code.claude.com/docs/en/sub-agents) 在一个会话内部充当范围明确的助手，拥有独立上下文窗口和工具限制。它适合多个任务中反复出现的工作，例如验证应用是否按预期运行。

并行会话增加工程师能同时推进的任务数；子代理让每个会话专注于自身任务。工程师负责指导和审查所有工作。

**传统方式。** 一位工程师一次做一项任务，每天或每周有相当多时间花在构建、测试和评审者身上。等待时可以切换任务，但上下文切换太耗精力，很少有人愿意这样做。

**AI 原生方式。** 一位工程师同时运行多个 Claude 会话，各有 worktree 和任务。重复工作交给拥有独立上下文与工具限制的子代理。工程师逐渐转向协调工作，最终转向建立和监控循环。

### 如何开始

**前置条件：** `CLAUDE.md`，因为所有会话都会读取它。第 4 阶段“测试”中的反馈回路也有帮助：会话能自查时，工程师就不必时时监督。

**基础设施：** Git 仓库，隔离来自 worktree；还需调整权限设置，使会话执行组织认为安全的命令时，无需一直等待批准提示。

### 如何执行

1. 工程师依据计划模式形成的计划，找出独立部分，将工作拆为修改不同文件的任务。共享文件的任务放在一个会话中先后运行。
2. 每个并行任务使用独立 worktree，例如一个终端运行 `claude --worktree feature-auth`，另一个运行 `claude --worktree fix-rate-limit`。worktree 是独立分支上的单独检出目录，避免会话在文件上冲突。
3. 从两三个会话开始比较合适。实际的上限是一个人能认真审查多少条工作线，只有评审跟得上时才增加会话。
4. 将重复工作制作成子代理，定义在 `.claude/agents/` 的 Markdown 文件中，写明名称、使用时机与可用工具。例如主代理完成后清除无谓复杂度的代码简化器、运行应用并检查行为的验证器，或探索代码后汇报结果、避免挤满主上下文的研究助手。定义提交到 Git，供全团队共享。

### 示例：.claude/agents/verifier.md

```markdown
---
name: verifier
description: Runs the app and checks the change works before the session
  reports done
tools: Bash, Read
---
Start the app with make run. Exercise the changed behavior and the two
nearest neighboring flows. Report what you ran, what you saw, and any
behavior that does not match plan.md. Do not fix anything; report only.
```

**示例中的文字。** `verifier` 在会话报告完成前运行应用、确认改动生效，可用工具只有 `Bash` 与 `Read`。使用 `make run` 启动应用，执行改动涉及的行为及最相近的两条流程。报告运行了什么、观察到什么，以及哪些行为不符合 `plan.md`。不修复，只报告。

### 治理方面的考虑

会话更多，产出也更多，因此控制措施必须来自仓库配置。仓库中的 Hooks 和权限设置应用于所有会话；会话所做的事情会被记录，并归属于运行会话的工程师。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 在评审质量保持稳定的条件下，每位工程师的并发会话数，使用 OpenTelemetry 导出统计；同时看一天中用于指导工作而非等待的时间比例。 |
| 滞后指标 | 每位工程师每周合并的改动数，并结合 PR 历史中的返工率一起解读。 |
