# 01 Plan：计划

想法不再等待别人整理成文。发起人用自己的话，一次记录意图，形成纳入版本控制、下一阶段能够据以行动的交付物。

## 用 intent.md 记录意图

启动软件开发过程的 `intent.md` 可以来自不同入口：某个人提出想法、有人提交工单，或告警揭示了一个事故。后者见第 6 阶段“维护”。

一个人有了想法，可以与 Claude 讨论，形成 Markdown 格式的初步规格。传统 SDLC 中，同一个人还需要说服产品团队的一位成员，一起整理这个想法，或请对方代为起草。

Claude 生成的初步规格便于人阅读，纳入版本控制后，下一阶段可以立即使用。这份初步规格保存为 `intent.md`。

无论意图来自事件触发还是 Agent，都要遵循相同步骤：提交前，产品负责人审阅并纠正 Agent 编写的 `intent.md`。

**传统方式。** 一个想法要经过待办条目、用户故事、故事点和细化会议，才有人能够采取行动。每次交接都会转移责任归属，工程团队最终收到的内容，已与发起人原本的意思隔了好几层。

**AI 原生方式。** 发起人与 Claude 讨论，把结果写成 `intent.md`，用自己的术语表达初步规格。交付物说明想要什么、为什么需要，以及要遵守哪些约束。重复流程则封装为 Skills。

### 如何开始

**前置条件：** 无。

**基础设施：** 让非工程人员能够使用 Claude，例如 claude.ai 或 [Cowork](https://claude.com/product/cowork)；约定 `intent.md` 模板；提供一个共享、纳入版本控制、由产品负责人关注的意图存放位置。单一产品最简单的做法是在产品仓库中建立 `intent/` 目录，使交付物链与据此产生的代码相邻。只有意图跨越多个仓库时，建立独立意图仓库的额外成本才值得承担；在 monorepo 中，它就是一个目录。第 3 阶段“开发实现”的侧栏说明，这个位置如何与已经承担记录职责的 Jira 或需求工具衔接。

这些基础设施由平台或工程团队一次性建立。技术人员需要创建意图存放位置，并决定谁有写入权限，因为许多参与者可能来自组织的其他部门。

仓库建好以后，没有 Git 经验的人无需直接使用 Git。借助 GitHub 等版本控制系统的连接器，Claude 可以在 claude.ai 或 Cowork 中代为提交 Markdown 文件。

### 如何执行

1. 发起人用自己的话向 Claude 描述问题，例如目前做不到什么、谁会受影响、改善后的状态是什么、哪些内容不在范围内。无需正式措辞。
2. 继续讨论，直到想法足够具体。Claude 会像分析师一样追问范围、用户、约束和成功标准。
3. 请 Claude 按组织模板写成 `intent.md`。技术人员可以把模板制作成 Skill，经负责人批准。内容可包括问题、预期结果、受影响用户与系统、约束和未决问题。
4. 发起人纠正 Claude 理解错误的地方。
5. 将 `intent.md` 提交到共享位置。作者与时间戳一同入档，产品负责人从这里接手。

```markdown
# Intent: claims status self-service
Author: J. Ortiz (claims operations). Status: draft.

## Problem
Customers phone the contact center to ask where their claim is.
Handlers spend roughly a third of call time on status-only queries.

## Proposed outcome
Customers see claim status, next step and expected date in the portal.

## Affected users and systems
Claims handlers, portal team, claims-core API.

## Constraints
No new PII in the portal session. Existing authentication only.

## Open questions
Do third-party loss adjusters need access too?
```

**示例中的文字。** 意图为“理赔状态自助查询”，作者为理赔运营人员 J. Ortiz，状态是草稿。问题是客户不断致电联系中心询问理赔进度，处理人员约三分之一的通话时间花在单纯查询状态上。预期结果是客户在门户看到理赔状态、下一步和预计日期。受影响对象包括理赔处理人员、门户团队和 `claims-core API`。约束是门户会话不新增个人身份信息（PII），只使用既有认证。未决问题是第三方理赔公估人是否也需要访问。

### 治理方面的考虑

证据是已提交的 `intent.md`，包含作者、时间戳和完整修订历史，记录在意图存放位置的 Git 历史中。产品负责人批准意图；决定是否进入第 2 阶段“设计”的接受或拒绝结果，通过交付物的合并记录或结束评审的记录保存。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 从首次对话到 `intent.md` 提交所经过的时间。通过意图存放位置的 Git 历史读取，其中记录作者与时间戳。预期是从持续数周的需求获取与细化周期，缩短到数小时。 |
| 滞后指标 | 意图存活率，即产品负责人接受进入第 2 阶段“设计”的 `intent.md` 比例，而非直接关闭的比例。接受或拒绝记录在合并或结束评审中。此外，统计同一次改动首次提交 `spec.md` 之后，`intent.md` 又被修改了多少次。 |
