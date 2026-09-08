#!/usr/bin/env python3
"""Serve the static site locally, with a project URL prefix and live reload."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import time
from urllib.parse import quote, unquote, urlsplit
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
ASSET_TYPES = {'.html', '.htm', '.css', '.js', '.mjs', '.json', '.md', '.txt',
               '.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.ico',
               '.woff', '.woff2', '.ttf', '.otf', '.pdf', '.mp4', '.webm', '.mp3'}
RELOAD_SCRIPT = r'''<script data-local-preview>
(() => {
  const revision = __REVISION__;
  const endpoint = __ENDPOINT__;
  const scrollKey = 'static-preview-scroll:' + location.pathname + location.search;
  try {
    const saved = sessionStorage.getItem(scrollKey);
    if (saved !== null) {
      sessionStorage.removeItem(scrollKey);
      addEventListener('load', () => {
        const style = document.documentElement.style;
        const previous = style.scrollBehavior;
        style.scrollBehavior = 'auto';
        scrollTo(0, Number(saved));
        requestAnimationFrame(() => { style.scrollBehavior = previous; });
      }, {once: true});
    }
  } catch (_) { /* Preview still works when browser storage is unavailable. */ }
  async function check() {
    try {
      if (!document.hidden) {
        const response = await fetch(endpoint, {cache: 'no-store'});
        if (!response.ok) return;
        const current = await response.json();
        if (current.revision !== revision) {
          try { sessionStorage.setItem(scrollKey, String(scrollY)); } catch (_) {}
          location.reload();
        }
      }
    } catch (_) { /* Keep the page readable; reconnect after the server returns. */ }
    finally { setTimeout(check, 1000); }
  }
  setTimeout(check, 1000);
})();
</script>'''


def asset_signature():
    digest = hashlib.blake2b(digest_size=12)
    for directory, folders, files in os.walk(ROOT):
        folders[:] = sorted(f for f in folders
                            if not f.startswith('.') and f not in {'node_modules', '__pycache__'})
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix.lower() not in ASSET_TYPES:
                continue
            try:
                stat = path.stat()
            except FileNotFoundError:  # An editor may be replacing this file.
                continue
            digest.update(str(path.relative_to(ROOT)).encode())
            digest.update(f'{stat.st_mtime_ns}:{stat.st_size}'.encode())
    return digest.hexdigest()


class PreviewServer(ThreadingHTTPServer):
    def __init__(self, port, base_path):
        self.base_path = base_path
        self.start_id = str(time.time_ns())
        self.signature = asset_signature()
        self.stopped = threading.Event()
        super().__init__(('127.0.0.1', port), PreviewHandler)
        self.watcher = threading.Thread(target=self.watch, daemon=True)
        self.watcher.start()

    @property
    def revision(self):
        return self.start_id + '-' + self.signature

    def watch(self):
        candidate = self.signature
        while not self.stopped.wait(0.5):
            current = asset_signature()
            # Wait for a stable scan so an editor's partial write is not displayed.
            if current == candidate and current != self.signature:
                self.signature = current
                print('文件已更新，浏览器将自动刷新。', flush=True)
            candidate = current

    def server_close(self):
        self.stopped.set()
        super().server_close()


class PreviewHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if args and str(args[1]) not in {'200', '301', '302'}:
            super().log_message(format, *args)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        self.respond(head_only=False)

    def do_HEAD(self):
        self.respond(head_only=True)

    def send_bytes(self, body, content_type, status, head_only):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def redirect(self, path, query):
        self.send_response(302)
        self.send_header('Location', quote(path, safe='/') + ('?' + query if query else ''))
        self.send_header('Content-Length', '0')
        self.end_headers()

    def html_bytes(self, path):
        original = path.read_bytes()
        script = RELOAD_SCRIPT.replace('__REVISION__', json.dumps(self.server.revision))
        script = script.replace('__ENDPOINT__', json.dumps(self.server.base_path + '__preview__/revision'))
        closing = re.search(br'</body\s*>', original, re.IGNORECASE)
        position = closing.start() if closing else len(original)
        return original[:position] + script.encode() + original[position:]

    def respond(self, head_only):
        url = urlsplit(self.path)
        requested = unquote(url.path)
        base = self.server.base_path
        if base != '/' and requested in {'/', base.rstrip('/')}:
            self.redirect(base, url.query)
            return
        if requested == base + '__preview__/revision':
            body = json.dumps({'revision': self.server.revision}).encode()
            self.send_bytes(body, 'application/json', 200, head_only)
            return
        if not requested.startswith(base):
            self.send_error(404, 'Use the project URL prefix: ' + base)
            return
        relative = Path(requested[len(base):])
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT) or any(p.startswith('.') for p in relative.parts):
            self.send_error(403)
            return
        if target.is_dir():
            if not requested.endswith('/'):
                self.redirect(requested + '/', url.query)
                return
            target = target / 'index.html'
        if not target.is_file():
            error_page = ROOT / '404.html'
            if error_page.is_file():
                self.send_bytes(self.html_bytes(error_page), 'text/html; charset=utf-8', 404, head_only)
            else:
                self.send_error(404)
            return
        if target.suffix.lower() in {'.html', '.htm'}:
            self.send_bytes(self.html_bytes(target), 'text/html; charset=utf-8', 200, head_only)
            return
        with target.open('rb') as source:
            self.send_response(200)
            self.send_header('Content-Type', self.guess_type(str(target)))
            self.send_header('Content-Length', str(os.fstat(source.fileno()).st_size))
            self.end_headers()
            if not head_only:
                shutil.copyfileobj(source, self.wfile)


def main():
    parser = argparse.ArgumentParser(description='本地预览静态网页，保存后自动刷新。')
    parser.add_argument('--port', type=int, default=4173)
    parser.add_argument('--base-path', default='/static_source/')
    parser.add_argument('--open', action='store_true', help='启动后打开默认浏览器')
    args = parser.parse_args()
    base = '/' + args.base_path.strip('/') + '/' if args.base_path.strip('/') else '/'
    if not re.fullmatch(r'/[A-Za-z0-9_/-]*/?', base) or '..' in base:
        parser.error('--base-path must be a URL path, such as /static_source/ or /')
    try:
        server = PreviewServer(args.port, base)
    except OSError as error:
        parser.exit(1, f'无法启动预览：{error}。可用 --port 4174 更换端口。\n')
    url = f'http://127.0.0.1:{server.server_port}{base}'
    print(f'本地预览：{url}\n保存网页或资源后自动刷新；按 Ctrl+C 停止。', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
