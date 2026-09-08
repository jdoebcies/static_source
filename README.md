# static_s

这是一个用于 GitHub Pages 发布的个人静态学习资料库。

## 本地实时预览

在 Mac 上双击根目录的 **本地预览.command**，会启动预览服务并打开浏览器。也可以在终端运行：

```bash
cd ~/code_sunjingyun_home/static_source
python3 scripts/preview.py --open
```

打开 <http://127.0.0.1:4173/static_source/>。编辑仓库里的 HTML、CSS、JavaScript 或页面引用的图片，保存后通常在1—2秒内自动刷新，并保留页面滚动位置。保持启动它的终端窗口运行；结束时按 `Ctrl+C`。

本地预览沿用项目站点的 `/static_source/` 路径，可以提前发现章节跳转与资源路径错误。需要查看手机布局时，可缩窄浏览器窗口，或使用浏览器的设备模拟模式。所有检查都在本地进行，不需要提交或推送 Git。

预览直接读取仓库中的成品 HTML。修改 Markdown 源稿后，仍需先生成对应 HTML。自动刷新脚本只添加到本地 HTTP 响应中，不会写进网页文件；GitHub Pages 的发布方式保持不变。

仅本地预览需要 Python 3.9 或更新版本，不需要安装第三方包。端口已被占用时使用 `--port 4174`；按站点根路径预览时使用 `--base-path /`。本地可验证内容、样式、交互与链接，GitHub 的部署、HTTPS和缓存状态仍需发布后确认。

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
