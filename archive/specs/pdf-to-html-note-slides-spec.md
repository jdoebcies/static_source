# PDF 转 HTML note-slides 规格

版本：v0.1  
日期：2026-05-27  
适用目录：`/mnt/smb/raid5/学习成长以后或过程中的的输出物/codex_cloud/static_sources/`

## 目标

把长 PDF、书籍、课程材料或报告转换成可直接静态发布的 HTML 学习材料。

默认产物是按章节拆分的单文件 HTML note-slides，每本书有一个总索引页，每章一个可翻页 HTML。最终进入 `static_sources/books/<书名>/`，由顶层 `index.html` 导航。

已验证样例：

- 《图形思考》：12 章，232 页 slides，12/12 通过 `check_deck.py`，0 warning。
- 《可观测性工程》：23 章，368 页 slides，23/23 通过 `check_deck.py`，0 warning。

## 目录定位

`static_sources` 是 GitHub Pages 风格的纯静态资料库，不依赖 Jekyll、Node.js、构建脚本或后端服务。

目录约定：

```text
/mnt/smb/raid5/学习成长以后或过程中的的输出物/codex_cloud/static_sources/
  index.html
  README.md
  .nojekyll
  404.html

  books/
    <书名>/
      index.html
      README.md
      CHAPTER_INDEX.md
      chapter_manifest.json
      chapters/
        <chapter-slug>-note-slides.html

  topics/
    <专题名>/
      index.html

  archive/
    reports/
      <书名>/
        final_summary.json
        final_check_report_*.txt
    specs/
      pdf-to-html-note-slides-spec.md
```

规则：

1. 一本书或章节化 PDF 放入 `books/<书名>/`。
2. 单篇主题、文章、访谈放入 `topics/<专题名>/`。
3. 生成报告、验收记录和规格文档放入 `archive/`，不混进主阅读入口。
4. 顶层 `index.html` 是公开导航入口；新增书籍后需要单独更新该导航。
5. GitHub Pages 发布后内容可能公网可访问，不放私人、版权敏感或未经确认可公开的材料。

## 使用的 Skill

主工作流：

- `pdf-chapter-note-slides`

依赖工作流：

- `note-slides`

关键文件：

```text
/root/.openclaw/skills/pdf-chapter-note-slides/SKILL.md
/root/.openclaw/skills/pdf-chapter-note-slides/scripts/prepare_pdf_chapters.py
/root/.openclaw/skills/pdf-chapter-note-slides/scripts/build_collection_index.py
/root/.openclaw/skills/pdf-chapter-note-slides/references/worker-instructions.md
/root/.openclaw/skills/note-slides/SKILL.md
/root/.openclaw/skills/note-slides/scripts/check_deck.py
```

## 输入边界

开始前必须验证 PDF 可用性。

遇到以下情况必须停止并报告，不得自动找网络替代版本：

- PDF 加密、需要密码、DRM 锁定或权限阻塞。
- 文本提取为空、乱码严重或疑似纯扫描图。
- PDF 目录缺失，且无法可靠判断章节边界。
- 页面图片或章节切片无法生成。
- 单章 `source.md` 为空、乱码或缺关键页。

可继续的前提：

- PDF 能提取文本。
- 章节边界来自 PDF outline、目录页或用户提供的手动 ranges。
- 每章能生成 `source.md` 和必要的 `page-XXX.jpg`。

## 工作流

### 1. 检查 PDF

目标：

- 确认页数、目录、章节边界和文本提取质量。
- 判断是否需要用户提供密码、EPUB、OCR 授权或手动章节范围。

禁止：

- 用搜索引擎下载另一个版本替代。
- 用不同版次、不同译本、网页摘要替代源 PDF。

### 2. 准备章节切片

默认先生成 workspace artifact：

```text
/root/.openclaw/workspace/artifacts/<pdf-slug>/
```

推荐命令：

```bash
python3 /root/.openclaw/skills/pdf-chapter-note-slides/scripts/prepare_pdf_chapters.py \
  --pdf /path/to/source.pdf \
  --out /root/.openclaw/workspace/artifacts/<pdf-slug> \
  --skip-title-regex '书名页|版权页|目录'
```

输出：

```text
source.pdf
chapter_manifest.json
CHAPTER_INDEX.md
chapters/<chapter-slug>/source.md
chapters/<chapter-slug>/page-XXX.jpg
```

如果目录不可靠，先写 `chapters.json`：

```json
[
  {"slug":"00-preface","title":"前言", "start":8, "end":24},
  {"slug":"01-chapter-one","title":"第一章", "start":25, "end":48}
]
```

页码规则：PDF 页码，1-based，闭区间。

### 3. 分批生成章节 HTML

默认每批 3 到 4 个 worker。章节长、图多、提取质量差时缩小批次。

每个 worker 只处理一个章节：

```text
Read /root/.openclaw/skills/pdf-chapter-note-slides/references/worker-instructions.md
Chapter title: <title>
Slug: <slug>
source.md: <chapter-dir>/source.md
output_dir: <chapter-dir>
Output: <slug>-note-slides.html
```

Worker 要求：

- 不读整本 PDF，只读本章 `source.md` 和本章 page images。
- 保留章节原顺序。
- 保留练习、例子、步骤、方法、总结和转折。
- 图形、流程、框架、矩阵类内容尽量用 HTML/CSS/SVG 重画。
- 每页必须有 `data-theme`、`data-screen-label`、`data-source`。
- `data-source` 必须指向 PDF 页或章节锚点，例如 `p40 课程1`。
- 输出单文件 HTML。

章节页数参考：

- 8 PDF 页以内：10 到 14 slides。
- 9 到 18 PDF 页：14 到 22 slides。
- 19 PDF 页以上：18 到 28 slides。

### 4. 单章验证

每个章节 HTML 必须运行：

```bash
python3 /root/.openclaw/skills/note-slides/scripts/check_deck.py --input <html>
```

P0 错误必须修复。warning 需要人工判断；明显问题直接修复。

常见问题：

- 自定义图形 class 叫 `dot` 触发导航点误判，应改为 `point`、`node` 或带命名空间的 class。
- 长 deck 缺核心总结页，应补一页真实总结，或把已有收束页显式标成总结。
- 图形书只做文字摘要会丢失材料价值，应重画关键图。

### 5. 父任务总验收

所有章节完成后，父任务必须重新批量检查：

```bash
find /root/.openclaw/workspace/artifacts/<pdf-slug>/chapters -maxdepth 2 -name '*-note-slides.html' | sort > /root/.openclaw/workspace/artifacts/<pdf-slug>/html_files.txt
while read -r f; do
  python3 /root/.openclaw/skills/note-slides/scripts/check_deck.py --input "$f"
done < /root/.openclaw/workspace/artifacts/<pdf-slug>/html_files.txt
```

验收标准：

- 每个章节 HTML 存在。
- 每个章节 `check_deck.py` 通过。
- `final_summary.json` 中章节数、slide 总数与目录一致。
- `index.html` 能链接到所有章节。
- 顶层 `static_sources/index.html` 如需公开导航，新增对应卡片。

### 6. 归档到 note-slides

长期归档目录：

```text
/mnt/smb/raid5/学习成长以后或过程中的的输出物/note-slides/<主题>/<书名>/
```

推荐命令：

```bash
python3 /root/.openclaw/skills/pdf-chapter-note-slides/scripts/build_collection_index.py \
  --source-root /root/.openclaw/workspace/artifacts/<pdf-slug> \
  --dest /mnt/smb/raid5/学习成长以后或过程中的的输出物/note-slides/<主题>/<书名> \
  --title '<书名>' \
  --check-deck /root/.openclaw/skills/note-slides/scripts/check_deck.py
```

该步骤会生成：

```text
README.md
index.html
CHAPTER_INDEX.md
chapter_manifest.json
chapters/*.html
final_summary.json
final_check_report_*.txt
```

### 7. 发布到 static_sources

把已验收产物同步到：

```text
/mnt/smb/raid5/学习成长以后或过程中的的输出物/codex_cloud/static_sources/books/<书名>/
```

推荐映射：

```text
note-slides/<主题>/<书名>/index.html              -> static_sources/books/<书名>/index.html
note-slides/<主题>/<书名>/README.md               -> static_sources/books/<书名>/README.md
note-slides/<主题>/<书名>/CHAPTER_INDEX.md        -> static_sources/books/<书名>/CHAPTER_INDEX.md
note-slides/<主题>/<书名>/chapter_manifest.json   -> static_sources/books/<书名>/chapter_manifest.json
note-slides/<主题>/<书名>/chapters/*.html         -> static_sources/books/<书名>/chapters/*.html
note-slides/<主题>/<书名>/final_summary.json      -> static_sources/archive/reports/<书名>/final_summary.json
note-slides/<主题>/<书名>/final_check_report*.txt -> static_sources/archive/reports/<书名>/
```

发布后检查：

```bash
git -C /mnt/smb/raid5/学习成长以后或过程中的的输出物/codex_cloud/static_sources status --short
```

注意：`static_sources` 是独立 Git 仓库。提交前要确认工作区是否已有无关改动，不能覆盖他人改动。

## 顶层导航规则

新增书籍后，在 `static_sources/index.html` 的 `书籍与章节资料` 区域添加卡片：

```html
<a class="item" href="books/<书名>/">
  <strong><书名></strong>
  <span>按章节拆分的 note-slides，包含章节索引、清单和 HTML 幻灯片。</span>
  <em class="tag">book</em>
</a>
```

新增专题后，在 `专题资料` 区域添加卡片，链接到 `topics/<专题名>/`。

导航更新后最小检查：

- 打开顶层 `index.html`，确认链接路径存在。
- 打开 `books/<书名>/index.html`，确认章节卡片路径存在。
- 任意抽查 2 到 3 个章节 HTML。

## 完成定义

一本 PDF 转 HTML 任务完成时，必须交付：

1. `static_sources/books/<书名>/index.html`
2. `static_sources/books/<书名>/chapters/*.html`
3. `static_sources/books/<书名>/README.md`
4. `static_sources/books/<书名>/CHAPTER_INDEX.md`
5. `static_sources/books/<书名>/chapter_manifest.json`
6. `static_sources/archive/reports/<书名>/final_summary.json`
7. `static_sources/archive/reports/<书名>/final_check_report_*.txt`
8. 顶层 `static_sources/index.html` 已按需加入导航卡片
9. 所有章节 `check_deck.py` 通过，warning 已处理或明确记录

最终汇报必须包含：

- 书籍索引路径
- 章节数量
- slide 总数
- `check_deck.py` 结果
- 是否已进入顶层导航
- 未解决的来源缺口或图形简化

## 经验约束

- 大 PDF 必须按章节切分，不把整本书塞给一个上下文。
- 图形书、流程书、架构书不能只做文字总结，关键图要重画。
- 先生成 workspace artifact，再归档到 note-slides，再发布到 static_sources。
- `note-slides` 是阅读产物，`static_sources` 是发布面。
- `archive/reports/` 存验收证据，主阅读入口只保留读者需要打开的 HTML。
