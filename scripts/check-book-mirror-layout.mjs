#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const booksRoot = path.join(root, "books");
const failures = [];
const results = [];

for (const name of fs.readdirSync(booksRoot)) {
  const bookRoot = path.join(booksRoot, name);
  const manifestPath = path.join(bookRoot, "reading-manifest.json");
  if (!fs.existsSync(manifestPath)) continue;
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const pages = [path.join(bookRoot, "index.html"), ...manifest.units.map((unit) => path.join(bookRoot, unit.html))];
  const bookFailures = [];
  for (const page of pages) {
    if (!fs.existsSync(page)) {
      bookFailures.push({ page, check: "exists" });
      continue;
    }
    const html = fs.readFileSync(page, "utf8");
    const checks = {
      format_marker: html.includes('content="reading-package-v1"') && html.includes('data-book-mirror-layout="reading-package-v1"'),
      chapter_layout: html.includes('<div class="shell') && html.includes("<aside><details><summary>本页目录</summary>"),
      single_main_title: (html.match(/<main>[\s\S]*?<h1[ >]/g) || []).length === 1,
      palette: html.includes("--ink:#2d3142") || html.includes("--ink: #2d3142"),
      mobile: html.includes("max-width:850px") || html.includes("max-width: 850px"),
      no_slide_runtime: !/(RAW_SLIDES|data-template-version="4\.5\.0"|class="stage"|note-slides)/i.test(html),
      portable: !/(file:\/\/|\/Users\/|X-Amz-|BOOKMIRROR_IMAGE_|\[待补\])/i.test(html),
    };
    for (const [check, pass] of Object.entries(checks)) {
      if (!pass) bookFailures.push({ page, check });
    }
    for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      const link = match[1];
      if (/^(https?:|data:|#|mailto:)/.test(link)) continue;
      const clean = decodeURIComponent(link.split("#")[0]);
      let target = path.resolve(path.dirname(page), clean);
      if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, "index.html");
      if (!fs.existsSync(target)) bookFailures.push({ page, check: "internal_link", link });
    }
  }
  if (pages.length !== manifest.units.length + 1) bookFailures.push({ check: "page_count" });
  failures.push(...bookFailures.map((failure) => ({ book: name, ...failure })));
  results.push({ book: name, units: manifest.units.length, pages: pages.length, status: bookFailures.length ? "fail" : "pass" });
}

const receipt = { status: failures.length ? "fail" : "pass", books: results.length, results, failures };
console.log(JSON.stringify(receipt, null, 2));
if (failures.length) process.exit(1);
