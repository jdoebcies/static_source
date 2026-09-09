# Book Mirror HTML 布局

`books/` 下由书镜生成的 HTML 统一采用《软件设计的哲学》《架构整洁之道》确定的章节式阅读布局。

## 页面结构

- 书籍根目录的 `index.html` 是全书导航。
- 每个阅读单元位于 `chapters/<unit-id>/`，同时保留 `chapter.md` 与 `index.html`。
- 桌面端左侧为吸顶的本页目录，右侧为连续正文；移动端目录折叠到正文上方。
- 章节页底部提供上一篇、下一篇；配图可点击放大；表格在窄屏下横向滚动。
- HTML 内联统一样式与交互，GitHub Pages 不依赖构建服务或外部资源。

## 内容边界

HTML 从当前书镜 Markdown 生成，完整保留原书回顾、主题讲解、理解检查和来源边界。旧 HTML、旧 Note Slides 和历史导航只用于覆盖前盘点，不作为正文输入。

书镜 HTML 必须带有：

```html
<meta name="book-mirror-html-format" content="reading-package-v1">
<body data-book-mirror-layout="reading-package-v1">
```

页面出现 `RAW_SLIDES`、演示舞台或逐页幻灯运行时即不合格。

## 单一视觉基线

- 样式源：`assets/css/book-mirror-reading.css`
- 交互源：`assets/js/book-mirror-reading.js`
- 背景：`#f5f5f5`
- 正文：`#2d3142`
- 链接：`#b9481a`
- 桌面正文：230px 目录 + 自适应正文，最大宽度 1200px
- 移动断点：850px

发布前运行：

```bash
node scripts/check-book-mirror-layout.mjs
```

检查必须覆盖所有含 `reading-manifest.json` 的书籍目录，并确认章节数量、内部链接、格式标记和旧演示运行时均符合要求。
