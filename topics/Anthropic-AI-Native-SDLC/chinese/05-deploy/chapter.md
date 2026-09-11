# 05 Deploy：部署

评审双向进行，治理在 Agent 行动时就被执行。Agent 可以完成生产关口之前的工作，不能自行越过这一关口。

## 把 AI 接入 PR 评审回路

Claude 既提出评审意见，也接受评审。它依据组织政策检查新 PR，并处理自己 PR 上的评审意见。工程师因此可以在 PR 评审中聚焦行为，也就是判断意图与风险。

**传统方式。** 评审能力按人的产出规划。PR 等待评审者通读全部内容，评审质量随负荷变化，作者不断追问进度，积压却持续增加。

**AI 原生方式。** 所有 PR 都接受同一组评审，各项发现按严重程度排序。人的注意力提高一层，关注改动是否实现计划中的意图，以及风险是否可接受。

### 如何开始

**前置条件：** 已更新的 `CLAUDE.md`，见第 3 阶段“开发实现”；若评审要执行书面政策，还需要 Skills；以及已定义的子代理。

**基础设施：** 仓库已经安装 Claude 集成，可以是管理员启用的托管 [Code Review](https://code.claude.com/docs/en/code-review) 服务（研究预览版），也可以是在自己 CI 中运行的 [claude-code-action](https://code.claude.com/docs/en/github-actions)。必要时，通过 AWS Bedrock、Google Vertex 或 Microsoft Foundry 调用模型，部署选项见 CI/CD 部分。要求代码所有者批准的分支保护政策也值得配置。

### 如何执行

1. 托管 Code Review 服务是最快的起点。管理员启用服务并选择仓库。需要掌控流水线，或希望 API 调用沿用组织自己的云服务协议时，可通过 `claude-code-action` 在自己的 CI 中运行评审，接入方式见 CI/CD 部分。
2. 技术负责人在仓库根目录编写 `REVIEW.md`，按组织关心的问题划分评审轮次：缺陷与逻辑错误；安全与漏洞；是否符合需求规格（需求方法中的 `spec.md`）、实施计划（计划模式方法中的 `plan.md`）及设计原则。`REVIEW.md` 还定义什么属于 Important、什么属于 Nit，以及哪些内容跳过。
3. 技术负责人设置人工介入的阈值。评审发现本身不会自动批准或阻止 PR，分支保护仍要求代码所有者批准。若平台工程师想依据评审发现设定合并门槛，可以读取 check run 发布的机器可读严重程度计数。
4. 评审者或作者在评审评论中提及 `@claude` 时，Claude 处理评论并推送修复，PR 讨论串记录请求与改动。这条修复回路通过 `claude-code-action` 运行；托管服务中的 `@claude review` 则是请求重新评审。对于 Claude 创建的 PR，还可以让它持续跟进直至合并。团队用自定义斜杠命令封装循环，扫描未解决评论和失败检查，逐项处理、推送修复，直到 PR 全部检查通过，只等待代码所有者批准。
5. 评审发现反馈到 `CLAUDE.md`。同一错误第二次被指出时，在本次评审中把纠正说明写入 `CLAUDE.md`。由于评审也读取这个文件，从下一个 PR 开始就会发现这类错误。评审还会指出改动使 `CLAUDE.md` 过时的地方。
6. 技术负责人每月调整配置：为评审发现评分以改进评审，并在 `REVIEW.md` 中限制 Nit 的数量。生成路径及 CI 已经强制执行的检查项不再报告。

### REVIEW.md 示例

```markdown
# Review instructions

## Passes
Run three passes and tag each finding with its pass:
- Bugs: logic errors, broken edge cases, subtle regressions
- Security: injection risks, authentication gaps, PII in logs
- Compliance: the change matches spec.md, plan.md and our design principles

## What Important means here
Reserve Important for findings that would break behavior, leak data
or breach a policy. Style and naming are nits.

## Cap the nits
Report at most five nits per review; summarize the rest as a count.

## Do not report
Generated files under src/gen/ and anything CI already enforces.
```

**示例中的文字。** 评审分三轮，每项发现注明轮次。Bugs 检查逻辑错误、边界问题和细微回归；Security 检查注入风险、认证缺口和日志中的 PII；Compliance 检查改动是否符合 `spec.md`、`plan.md` 和设计原则。Important 只用于会破坏行为、泄漏数据或违反政策的发现，风格和命名属于 Nit。每次最多报告 5 个 Nit，其余只汇总数量。不报告 `src/gen/` 下的生成文件及 CI 已强制执行的事项。

### 治理方面的考虑

职责分离得以保留，因为写代码的 Agent 没有批准自己代码的路径。`REVIEW.md` 中的政策应用于所有 PR，发现、修复、评分和批准都记录在 PR 历史中，因此 PR 就是审计记录。人参考评审发现，通过分支保护机制批准。

这些控制措施如何在生产规模下组合，参见 [Anthropic 如何保护其 AI 原生软件开发生命周期](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle)。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 首次评审所需的时间，预期缩短至数分钟；以及无需人修改分支就能解决的评审评论比例。数据直接记录在 Git 中。 |
| 滞后指标 | 比较合并前发现的缺陷与漏洞，以及逃逸到生产环境的问题，取自 PR 历史和事故追踪系统。 |

## 把 Hooks 用作审批关口

第 3 阶段“开发实现”中，Hooks 用作无需人介入、允许或阻止动作的保护措施。Hook 也可以发起询问，暂停动作，直到某个指定的人批准。这正是发布审批所需的机制。

这项方法放在第 5 阶段“部署”，是因为发布关口最直观，但 Hooks 并不限于部署：Claude 在哪里行动，它们就可以在哪里运行。例如，在开发阶段没有变更工单时阻止编辑迁移和基础设施文件，在测试阶段阻止 Agent 于修复任务中编辑测试文件。

### 如何开始

**前置条件：** 无。

**基础设施：** 一份书面清单，列明变更流程要求的批准事项。

### 如何执行

1. 工程管理者会同变更管理和合规人员，列出必须保留的人工审批关口，例如变更管理签字、发布授权和受保护路径的编辑。
2. 平台工程师将每个关口写成 Hook，即 Claude 行动前运行的脚本，能够允许、询问或阻止动作。
3. 团队 Hooks 放在 Git 中的 `.claude/settings.json`；不可协商的 Hooks 放入平台或 IT 管理员负责的托管设置，个人工程师无法关闭。
4. 阻止动作时应说明原因：当 Hook 阻止操作，Claude 的输出中应显示理由及获得批准的路径。

### .claude/settings.json 示例

```json
{
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Bash",
          "hooks": [
            { "type": "command",
              "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/production-gate.sh" }
          ]
        }
      ]
    }
}
```

**示例说明。** 该配置在 `PreToolUse` 事件中匹配 `Bash`，执行项目中的 `.claude/hooks/production-gate.sh`。

### 示例：.claude/hooks/production-gate.sh

```bash
#!/bin/bash
# Production deploys require a named release authorization
cmd=$(jq -r '.tool_input.command' < /dev/stdin)
if [[ "$cmd" == *"deploy"* && "$cmd" == *"production"* ]]; then
   if [ -z "$RELEASE_APPROVAL" ]; then
     echo "Production deploys need a release authorization." >&2
     exit 2 # exit 2 blocks the action; the message goes to Claude
   fi
fi
exit 0
```

**示例中的文字与条件。** 注释说明生产部署需要具名发布授权。脚本从标准输入读取工具命令；命令同时包含 `deploy` 与 `production`，且 `RELEASE_APPROVAL` 未设置或为空时，输出“生产部署需要发布授权”，返回 2 以阻止动作，消息会交给 Claude。其他情况返回 0。

### 治理方面的考虑

Hooks 就是审批关口。关口条件对所有人、每次动作都执行，允许和阻止的决定带时间戳留档。关口还明确什么算作批准，例如已批准的变更工单，或发布负责人的签字。

## 完整示例：受监管企业的托管设置

配置由平台团队通过 MDM 或管理控制台部署。工程师无法编辑或覆盖其中任何内容。

```json
{
  "permissions": {
     "deny": [
        "Read(.env*)", "Read(./secrets/**)",
        "WebFetch", "Bash(curl *)", "Bash(wget *)"
     ],
     "allow": [
        "Bash(git *)", "Bash(make build)",
        "Bash(make test)", "Bash(make lint)"
     ],
     "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true,
  "sandbox": {
     "enabled": true,
     "failIfUnavailable": true,
     "allowUnsandboxedCommands": false,
     "network": { "allowedDomains": ["git.internal.example.com",
"registry.npmjs.org"] },
     "credentials": {
        "files": [
          { "path": "~/.ssh", "mode": "deny" },
          { "path": "~/.aws/credentials", "mode": "deny" }
        ],
        "envVars": [ { "name": "GITHUB_TOKEN", "mode": "deny" } ]
     }
  },
  "allowManagedHooksOnly": true,
  "disableSideloadFlags": true,
  "allowManagedMcpServersOnly": true,
  "strictKnownMarketplaces": [
     { "source": "github", "repo": "example-corp/approved-plugins" }
  ],
  "requiredMinimumVersion": "2.1.193"
}
```

### 各项配置对应什么控制作用

- `permissions.deny` 阻止秘密进入 Agent 上下文，并阻止通过工具任意向外访问网络；`permissions.allow` 则预先批准安全的内部工作循环，避免禁止列表造成反复确认的疲劳。
- `disableBypassPermissionsMode` 与 `allowManagedPermissionRulesOnly` 结合，使工程师、项目文件或命令行标志都不能扩大规则允许的范围。
- `sandbox` 填补单靠 permissions 无法覆盖的缺口。工具层禁止 `WebFetch`，不能阻止 Shell 命令访问网络；操作系统级的域名允许列表则直接限制网络外连。
- `failIfUnavailable` 和 `allowUnsandboxedCommands` 使沙箱成为必须通过的关口：沙箱无法初始化时，Claude Code 拒绝启动；命令在沙箱内失败后，不能转到沙箱外重试。
- `credentials` 填补 deny 规则留下的空隙。`permissions.deny` 管理 Claude 的文件工具，但沙箱中的 Shell 命令默认仍可能读取 `~/.ssh` 或 `~/.aws/credentials`。这一配置块拒绝这些读取，并从每个沙箱命令的环境中移除指定秘密。
- `allowManagedHooksOnly` 保证这里定义的审批关口是唯一会运行的 Hooks，本地配置不能新增或替换它们。
- `disableSideloadFlags` 与 `strictKnownMarketplaces` 结合，保证工程师机器上的每个 Skill、Agent、Hook 和 MCP server 都来自组织批准的插件市场，而非用户主目录。
- `allowManagedMcpServersOnly` 把 Agent 的工具范围限定为平台团队管理的允许列表。
- `requiredMinimumVersion` 拒绝启动低于获准最低版本的程序，保证执行这些控制措施的是组织实际评估过的版本。

将以上配置视为需要按实际情况调整的起点，不是建议直接照抄的配置。每一项禁止都会牺牲相应能力，合适的平衡取决于仓库的数据分类。[设置参考](https://code.claude.com/docs/en/settings)说明了每个配置键，包括仅能用于托管设置的键。

### 如何衡量 Hooks 本身

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 在各个审批关口等待的时间。每次 Hook 决定都带着时间戳和允许或阻止的结果写入 OpenTelemetry 导出，因此能看到每个关口的等待。 |
| 滞后指标 | 比较采用 Hooks 前后，违反关口要求却进入生产的问题，数据来自事故追踪系统。 |

## CI/CD 集成与部署

在 CI/CD 流水线中以非交互方式运行 Claude Code，用沙箱保护长时间运行的 Agent，通过 MCP 集成开放部署能力，并在 Agent 真正需要回滚之前演练好回滚路径。

**传统方式。** 流水线运行确定性脚本，凡是需要判断的事情都等人处理，例如不稳定测试分诊、编写变更日志、判断构建为何失败。部署和回滚是人在压力下照着执行的操作手册。

**AI 原生方式。** Claude 在流水线中以非交互方式完成判断步骤，运行于沙箱，使用限范围的凭据。部署工具通过 MCP 提供给 Agent，因此写出并测试改动的工作流，也能够在组织按环境设置的关口内完成发布和回滚。

### 如何开始

**前置条件：** 已将 Claude 接入 PR 评审回路，并将 Hooks 用作审批关口。必须先有这些关口，才能让自动化加快通过它们的工作。

**基础设施：** 安装了 `claude-code-action` 的 CI 平台，或任何能够调用 `claude -p` 的 runner；通过 API 接入模型，若流量必须走组织的云服务协议，则使用 Bedrock、Foundry 或 Vertex；提供部署目标的 MCP servers；为 Agent 作业配置沙箱，并且不长期持有生产凭据。

### 如何执行

1. 平台工程师从只读判断开始。在流水线作业中使用 `claude -p`，对失败构建分诊、概括不稳定测试，或起草变更日志。
2. 在现有关口后增加写入步骤，例如修复 lint、更新生成文档，或通过 `@claude` 处理评审意见。Agent 写出的内容都以 PR 经过分支保护，没有直接推送 main 的路径。
3. 在沙箱中执行。Agent 作业运行在受网络政策约束的容器中，使用短期、限范围的令牌，默认不持有生产凭据。
4. 经 MCP 暴露部署、状态和回滚工具，按环境限制范围，使 Agent 的部署权限由允许列表限定，而不是交给它一份带有凭据的 Shell 脚本。
5. 按环境划分自主程度。开发环境中，Agent 可以自由部署；生产环境中，Agent 准备发布，由发布负责人授权，Hook 执行生产关口。预发布环境处于两者之间。
6. 回滚应当是流水线里演练最充分的路径：Agent 可以用单一命令运行，并定期在预发布环境演练。第 6 阶段“维护”中的循环会在指标越出控制带时调用它，因此必须提前验证。

### 流水线步骤示例

```yaml
- name: Triage failed build
  if: failure()
  run: >
    claude -p "Read the build log at out/build.log. Identify the most
    likely cause, say whether the failure looks flaky or real, and write a
    three-line summary for the PR thread." >> triage.md
```

**示例中的提示词。** 读取 `out/build.log` 中的构建日志，找出最可能的原因，判断失败看起来是不稳定失败还是真实问题，并为 PR 讨论串写一份三行摘要。该步骤仅在失败时执行，输出追加到 `triage.md`。

### 治理方面的考虑

基本原则是：Agent 可以行动到生产关口之前，不能自行越过。以下控制措施执行这一原则：

- 分支保护让 Agent 的任何写入都通过 PR，没有直达 main 的路径。
- 生产部署 Hook 在指定发布负责人授权前阻止发布。每次非交互运行使用 Agent 自己的身份，因此流水线日志可以区分 Agent 做了什么，以及触发它的工程师做了什么。
- 按环境划分权限等级，决定 Agent 在到达关口前能够完成多少工作。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 无需呼叫人来处理，就完成分诊的流水线失败比例，数据来自 CI/CD 日志。 |
| 滞后指标 | DevOps Research and Assessment（DORA）指标，CI 系统和部署工具已经输出这些数据。 |
