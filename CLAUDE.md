# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website for 84-CS (84-cs.com), a software development and infrastructure company in Ljubljana, Slovenia. The site consists of:
- Main landing page (pure HTML/CSS/JS with Tailwind CDN)
- Static blog system (Python-based Markdown-to-HTML generator)
- Hydrate app privacy policy page

## Development Commands

### Blog System

**IMPORTANT**: Always activate the virtual environment before working with the blog:
```bash
source .venv/bin/activate
```

**Build blog posts**:
```bash
python build_blog.py
```

This converts Markdown files in `_posts/` to static HTML in `blog/`. Only posts with `published: true` in their front-matter are built.

**Install dependencies** (if needed):
```bash
pip install -r requirements.txt
```

## Architecture

### Two Distinct Systems

1. **Main Site** (`index.html`, `hydrate/policy.html`)
   - Pure HTML with inline CSS/JavaScript
   - No build process required
   - All dependencies via CDN (Tailwind, Google Fonts)
   - Edit directly and commit

2. **Blog System** (Python generator)
   - **Source**: Markdown files in `_posts/` with YAML front-matter
   - **Output**: Static HTML in `blog/` and `blog/posts/`
   - **Build tool**: `build_blog.py` (uses Jinja2, python-frontmatter, markdown)
   - **Templates**: Embedded in `build_blog.py` (BLOG_INDEX_TEMPLATE, POST_TEMPLATE)
   - **Dependencies**: Only needed for local build; GitHub Pages serves static HTML

### Blog Post Structure

Posts in `_posts/` use YAML front-matter:
```yaml
---
title: "Post Title"
date: 2025-01-15
tags: [tag1, tag2]
published: true
---
```

- Filename becomes the slug (e.g., `2025-01-15-post-title.md` → `/blog/posts/2025-01-15-post-title.html`)
- `published: false` posts are skipped during build
- Excerpt auto-generated from first paragraph

### Design System

- **Fonts**: Inter (body), JetBrains Mono (headings/code)
- **Accent color**: `#3b82f6` (blue)
- **Custom classes**: `.blue-underline` (section titles), `.scroll-indicator` (hero section)
- **Navigation**: Hash-based smooth scrolling with header offset compensation

## Deployment

GitHub Pages deployment via `main` branch. Domain configured in `CNAME` file.

**Workflow**:
1. For main site: Edit HTML directly, commit, push
2. For blog: Edit Markdown in `_posts/`, run `python build_blog.py`, commit generated HTML, push

## Key File Locations

- Main landing page sections: index.html:137-439 (services, products, about, contact)
- Blog templates: build_blog.py:22-193
- Blog posts source: `_posts/*.md`
- Generated blog pages: `blog/index.html`, `blog/posts/*.html`
