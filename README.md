# static_s

这是一个用于 GitHub Pages 发布的个人静态学习资料库。

## 发布定位

- 仓库建议保持私有，但 GitHub Pages 发布后的站点内容会在公网可访问。
- 发布源建议设置为 `main` 分支的 `/` 根目录。
- 本仓库不依赖 Jekyll、Node.js、构建脚本或后端服务，所有页面都应能以静态文件方式直接访问。

## 目录约定

```text
/
  index.html            # 顶层导航入口
  .nojekyll             # 禁用 GitHub Pages 默认 Jekyll 处理
  README.md             # 仓库说明
  404.html              # 简单 404 页面

  books/                # 一本书或一组章节化学习材料
    <书名>/
      index.html
      README.md
      CHAPTER_INDEX.md
      chapter_manifest.json
      chapters/

  topics/               # 单篇专题、独立知识点或非书籍型材料
    <专题名>/
      index.html

  assets/               # 全站共享静态资源
    css/
    js/
    images/

  archive/              # 生成报告、验收记录等非主阅读入口
    reports/
```

## 内容添加规则

1. 新增一本书时，放入 `books/<书名>/`，并提供该书自己的 `index.html`。
2. 新增单篇专题时，放入 `topics/<专题名>/`，并提供该专题自己的 `index.html`。
3. 图片、附件、Markdown、JSON 等静态文件可以直接保留，但对外阅读入口优先提供 HTML。
4. 生成检查报告、摘要 JSON 等过程产物放入 `archive/`，避免干扰学习入口。
5. 所有链接优先使用相对路径，避免仓库名变化后链接失效。

