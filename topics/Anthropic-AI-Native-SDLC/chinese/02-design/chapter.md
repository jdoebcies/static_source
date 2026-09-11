# 02 Design：设计

需求和设计合并到一次会话中。政策在编写规格时就得到应用，无需等到几周后的评审才发现问题。

## 需求与设计

产品负责人批准后，Claude 读取获准的 `intent.md`，生成需求与设计规格。组织针对品牌、安全、合规和用户体验编写的 [Skills](https://code.claude.com/docs/en/skills)，为这一过程提供指导。

产品负责人负责审阅规格，无需自己起草。目标是生成一份工程团队可以据以制定计划的规格，并把需要关注的问题标出来。

前端工作最容易说明这一点。`intent.md` 获准后，产品负责人据此在 [Claude Design](https://claude.com/product/design)（测试版）中制作设计稿，反复调整，再导出给 Claude Code 实现。

**传统方式。** 需求和设计是不同团队负责的两个阶段。分析师把想法正式写成需求，设计师再把需求解读成设计。这种分离是为了明确责任，但过程缓慢，也会损失信息。

**AI 原生方式。** 两个阶段在一次提示驱动的会话中完成。Claude 读取 `intent.md`，按照组织 Skills 的约束生成需求与设计规格，并标出疑虑。

### 如何开始

**前置条件：** 已写好 `intent.md`，并将品牌、安全、合规和用户体验政策编写为 Skills。

**基础设施：** 一位能够使用 Claude 的产品负责人。执行这一步不需要工程技能。

### 如何执行

1. 产品负责人启动能够访问组织 Skills 的会话，并附上 `intent.md`。
2. 提示词指向 `intent.md`，列明约束，要求标出疑虑。最初手动运行，再将其固化为组织级斜杠命令。之后，以意图存放位置中的 `intent.md` 获准为触发条件，在合并时启动非交互作业，加载组织 Skills 完成处理，再以 PR 提交 `spec.md`。第 5 阶段“部署”的 CI/CD 方法说明了接入机制。做到这一步后，产品负责人首次介入就是评审。
3. 同一位产品负责人对照原想法审阅规格：它解决了提出的问题吗？`intent.md` 中的未决问题得到回答了，还是被明确带到后续阶段？
4. 先处理标出的疑虑，因为它们正是分析师原本会升级处理的问题。工程团队看到规格前，产品负责人逐项与相应政策负责人解决。
5. 将 `spec.md` 与 `intent.md` 放在一起提交。两份文件记录最初提出什么要求，以及最终决定了什么。
6. 产品负责人决定规格与意图是否进入开发实现；对于组织认定为较高风险的事项，咨询技术负责人。这个决定始终由人作出。接受规格后，才会启动第 3 阶段“开发实现”中的计划模式。

### 提示词示例

```markdown
Read the attached intent.md and produce a requirements and design spec for integrating it into our existing codebase. Apply the skills available to you so the plan conforms to our brand guidelines, security policies and UX standards. Document the spec fully as spec.md, ready to hand to the engineering team. Describe clearly any areas of concern, especially where you cannot satisfy contradicting policies.
```

**提示词中文。** 阅读所附的 `intent.md`，生成需求与设计规格，说明如何将需求整合进现有代码库。运用你能够使用的 Skills，使方案符合我们的品牌准则、安全政策和用户体验标准。把规格完整记录为 `spec.md`，准备交给工程团队。清楚描述所有疑虑，尤其是无法同时满足、相互冲突的政策。

### 治理方面的考虑

当前政策在编写规格时就被读取和应用，不必等到几周后的评审才发现问题。组织 Skills 对规格施加约束。规格、生成它的提示词，以及当时生效的 Skill 版本，都记录在版本控制系统中。产品负责人批准规格，并把标出的疑虑交给明确指定的政策负责人。

### 如何衡量

| 指标类型 | 定义与取数方式 |
| --- | --- |
| 领先指标 | 同一次改动中，`intent.md` 提交与 `spec.md` 提交之间的时间，取两个 Git 时间戳之差，与原先需求加设计的周期比较。 |
| 滞后指标 | 开发开始后的需求返工。统计同一次改动首次提交 `plan.md` 之后的 `spec.md` 提交次数，直接从 Git 日志获取。 |
