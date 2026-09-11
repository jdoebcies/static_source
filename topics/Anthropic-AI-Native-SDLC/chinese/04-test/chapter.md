# 04 Test：测试

每个会话都在人看到结果前检查自己的工作；引导 Agent 的配置，也像它写出的代码一样接受回归测试。

## 给 Claude 一个反馈回路

始终让 Claude 有办法验证自己的工作，例如测试、构建或截图差异。会话先自查、修正错误，再把结果交给工程师。

反馈回路不应与第 3 阶段“开发实现”中的验证子代理混淆。反馈回路贯穿整个任务，工作反复几次，它就跟着运行几次。验证子代理则是在会话认为工作完成后，使用新的上下文窗口执行最终检查的一种方式，让判断不受生成代码时那些假设的影响。

**传统方式。** 代码是否有效的信号到得很晚：CI 可能几分钟后才反馈，测试人员几天后才反馈，生产环境几周后才反馈。Agent 生成代码时，信号迟到意味着人必须检查它的全部产出，这个人就成了瓶颈。

**AI 原生方式。** 会话获得在人看到结果前自查的能力：运行测试、执行构建、获取截图。Claude 持续调整，直到检查通过，因此交给工程师的结果已经通过检查。建立这个反馈回路是运行会话的工程师的责任，以下步骤面向这位工程师。

### 如何开始

**前置条件：** 无。

**基础设施：** 能在本地各用一条命令运行的测试套件和构建。UI 工作尤其需要让 Claude 看见结果，可以使用浏览器工具，或通过 MCP 接入的截图工具。

### 如何执行

1. 如果目前检查工作需要一串命令和一些环境知识，就封装为 `make test` 或 `npm test` 这样的单一入口，失败时返回非零退出码。
2. 在 `CLAUDE.md` 的 Commands 小节列出每条命令，并提供正常输出的示例。
3. 给出可量化目标，让 Claude 不必追问就能自查。例如，“`test_status.py` 中全部测试通过”“截图与附件设计稿一致”“端点返回 200，且包含新字段”。
4. 修复缺陷时，先写会失败的测试。请 Claude 用测试复现缺陷，运行它，确认失败原因符合预期，再提交该测试。之后才让 Claude 在不修改测试的前提下使测试通过，并用最后一步所说的测试文件 Hook 执行这一限制。修复前已经存在、Agent 又不能改写的测试，证明缺陷已经消失。
5. UI 工作通过视觉检查完成反馈循环。给 Claude 浏览器或截图工具，提供设计稿，让它反复实现、截图、比较和调整。两三轮很正常，每一轮结果都应改善。
6. 把验证纳入“完成”的定义，指令放在 `CLAUDE.md`。报告任务完成前运行测试，并展示输出。
7. 反馈回路本身也要保护，因为修复代码的 Agent 不能削弱对这份代码的检查。可以通过 Hook 阻止它在修复任务中编辑测试文件；另一种办法是在评审时检查 diff，拒绝任何修改测试的变更。

### CLAUDE.md 验证小节示例

```markdown
## Verifying your work

- Build: make build (must finish with "Build succeeded")
- Test: make test (all green; never skip or delete a failing test)
- Lint: make lint (zero warnings)

Run all three before reporting any task complete, and paste the output.
If a test fails, fix the code, not the test.
```

**示例中的文字。** 构建命令 `make build` 必须以 `Build succeeded` 结束；`make test` 必须全部通过，不得跳过或删除失败测试；`make lint` 必须零警告。报告完成前运行三项检查，并贴出输出。测试失败时修复代码，不要修改测试。

### 治理方面的考虑

| 要回答的问题 | 原文要求 |
| --- | --- |
| 强制执行什么 | 报告完成前验证，并阻止 Agent 在修复时编辑测试文件。组织希望确保这些要求成立时，两者都通过 Hooks 执行。 |
| 证据是什么 | Claude 实际运行并贴出的 `make test` 原始输出、构建日志或截图差异，证据来自工具链。 |
| 记录在哪里 | 会话记录由 OpenTelemetry 导出转发到组织的可观测性系统；PR 的 check run 也保存记录，评审者和之后的审计人员都能看到。 |
| 谁批准 | 负责 PR 评审的代码所有者。机械检查的证据已经附上，评审者可以专注意图与风险。 |

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | Agent 编写的改动第一次运行 CI 的成功率，CI 系统已经支持统计。 |
| 滞后指标 | 每个 PR 的评审时间，取自 PR 元数据；测试接手过去由评审者发现的问题后，这个时间应当下降。另看从事故追踪系统获得的变更失败率。 |

## 在 CI 中持续运行 eval

Eval 是 AI 原生流程中与阶段关口 QA 对应的评估机制。实际做法是：每当 Agent 配置发生变化，就运行一套评估。换模型或改写提示词后，评估集告诉你，Agent 是否仍能以相同标准完成工作。

评估集应持续维护。随着模型进步，原本能区分表现的案例会失去区分作用，必须加入持续监测中出现的新案例。

根据使用情形，有些团队可能更愿意按固定周期离线评估，而非每次变更都运行。下面介绍持续评估的步骤。

### 如何开始

**前置条件：** `CLAUDE.md` 和第 4 阶段“测试”中的反馈回路。

**基础设施：** 能以非交互方式运行 Claude Code 的 CI，以及具备评估运行预算的 API Key。

### 如何执行

1. 平台工程师从近期工作中收集 20～50 个真实任务，以及它们的预期或已接受结果。
2. 将每项任务写成 eval，包括提示词和定义可接受结果的检查：测试通过、lint 无问题、行为不变、遵守政策。
3. 在 CI 中定期以非交互方式运行评估集，并在 `CLAUDE.md`、Skills 或 Hooks 改动时运行。这些配置引导 Agent 行为，应像代码一样接受回归测试。
4. 依据评估结果控制配置变更的合并。Skill 改动导致通过率下降时，先评审，再合并。
5. 每次生产事故都由负责该事故的团队写成一个 eval，留在套件中作为回归测试。

### 示例：.github/workflows/agent-evals.yml

```yaml
name: Agent evals
on:
  pull_request:
    paths: ['CLAUDE.md', '.claude/**']
  schedule:
    - cron: '0 2 * * *'
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @anthropic-ai/claude-code
      - name: Run eval suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          for eval in evals/*.json; do
            claude -p "$(jq -r '.prompt' $eval)" \
              --allowedTools "Read,Edit,Bash(make test)" \
              --output-format json > result.json
            ./evals/check.sh "$eval" result.json
          done
```

**示例中的文字。** 工作流名为 Agent evals，监听 `CLAUDE.md` 和 `.claude/**` 的 PR 变更，并每日定时运行。它检出代码、安装 Claude Code，从仓库 Secret 读取 API Key。随后遍历 `evals/*.json`，读取其中的提示词，在限定工具范围内运行 Claude，将结果写为 JSON，再用 `evals/check.sh` 检查每个任务。

### 治理方面的考虑

Eval 为 QA 提供能跟上 Agent 产出的关口。通过率阈值由合并检查强制执行；运行记录用于跨时间比较结果；拥有这项配置变更的团队负责批准。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 评估通过率随时间的变化，每次运行由套件报告；另看生产事故多久能转化为长期保留的 eval。 |
| 滞后指标 | 比较在 CI 中发现的回归与在生产中发现的回归，数据来自事故追踪系统。 |
