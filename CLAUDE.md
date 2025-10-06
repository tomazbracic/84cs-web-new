# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static website for 84-CS, a software development and infrastructure company based in Ljubljana, Slovenia. The website is a single-page application showcasing services, products, company information, and contact details.

## Architecture

**Technology Stack:**
- Pure HTML with embedded CSS and JavaScript
- Tailwind CSS via CDN (https://cdn.tailwindcss.com)
- Google Fonts: Inter (body) and JetBrains Mono (headings/code elements)

**Site Structure:**
- `index.html` - Main landing page with all sections (hero, services, products, about, contact)
- `hydrate/policy.html` - Privacy policy page for the Hydrate mobile app
- `assets/hydrate/icon-hydrate.png` - Hydrate app icon
- `CNAME` - Domain configuration for GitHub Pages (84-cs.com)

**Page Sections (index.html):**
1. Fixed header with navigation
2. Hero section with scroll indicator
3. Services section (Software Development, Infrastructure, System Architecture, AI Solutions)
4. Products section (divided into Proprietary Products and Side Projects)
5. About section
6. Contact section
7. Footer

## Key Design Patterns

**Smooth Scroll Navigation:**
- Anchor links use hash navigation (#services, #products, etc.)
- JavaScript handles smooth scrolling with header offset compensation
- Fixed header height is accounted for in scroll position calculations

**Styling Conventions:**
- Blue accent color: #3b82f6
- Monospace font (JetBrains Mono) for headings and brand elements
- Custom `.blue-underline` class for section titles (creates centered blue underline)
- Custom `.scroll-indicator` for hero section scroll hint

## Development Notes

**Python Environment:**
ALWAYS activate the virtual environment before working on the blog build process:
```bash
source .venv/bin/activate
```

The Python dependencies (in requirements.txt) are ONLY needed for the local build process. The generated HTML files are static and require no dependencies on GitHub Pages.

**Blog Build Process:**
1. Activate virtualenv: `source .venv/bin/activate`
2. Write blog posts as Markdown in `_posts/` directory
3. Run build script: `python build_blog.py`
4. Commit generated HTML files in `blog/` directory
5. Push to GitHub Pages

**Main Site (No Build Process):**
The main landing page (index.html) is a static site with no build step. All dependencies are loaded via CDN.

**Deployment:**
The site is configured for GitHub Pages deployment (as indicated by CNAME file). Any changes to HTML files are immediately reflected after git push to the main branch.

**Adding New Content:**
- New services: Add card to services grid in index.html:137-208
- New proprietary products: Add to grid in index.html:226-271
- New side projects: Add to grid in index.html:281-353
- Update contact info: Edit section at index.html:385-439

## Company Information

**84-CS Services:**
- Software Development (custom solutions)
- Infrastructure (scalable setup and management)
- System Architecture (robust design)
- AI Solutions (Agentic AI, n8n automation, RAG implementations)

**Technology Focus:**
- Elixir, Phoenix, LiveView
- Golang
- Nerves (IoT)
- Kafka, NATS (messaging infrastructure)

**Key Products:**
- IoT Connected Car Platform
- OTA Cloud Service
- Cyber Security Logs Dashboard
- Manufacturing Inventory System
- Electricity Trading Infrastructure

**Side Projects:**
- Tarock Counter (tarok.playfuldata.org)
- 123Math.online
- Hydrate mobile app (iOS, privacy-first hydration tracker)
