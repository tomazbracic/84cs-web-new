# 84-CS Website

Static website for 84-CS (84-cs.com), a software development and infrastructure company based in Ljubljana, Slovenia.

## Project Structure

This project consists of two main parts:

1. **Main Website** (`index.html`, `hydrate/policy.html`)
   - Pure HTML with Tailwind CSS (via CDN)
   - No build process needed
   - Edit directly and commit

2. **Blog System** (`blog/`)
   - Python-based static site generator
   - Markdown posts → HTML pages
   - Requires build step before deployment

## Initial Setup (First Time Only)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd 84cs-web-new
```

### 2. Set Up Python Environment with `uv`

```bash
# Initialize uv project
uv init

# Pin Python version to 3.14
uv python pin 3.14

# Create virtual environment with Python 3.14
uv venv --python 3.14

# Activate virtual environment
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Install required packages for the blog system
uv add python-frontmatter markdown jinja2
```

**Required packages:**
- `python-frontmatter` - Parse YAML front-matter in blog posts
- `markdown` - Convert Markdown to HTML
- `jinja2` - Template rendering engine

## Blog Workflow

### Writing a New Blog Post

1. **Create a new Markdown file** in the `_posts/` directory:

   ```bash
   touch _posts/2025-11-27-your-post-title.md
   ```

   **Filename format:** `YYYY-MM-DD-post-slug.md`

2. **Add YAML front-matter** at the top of the file:

   ```markdown
   ---
   title: "Your Post Title"
   date: 2025-11-27
   tags: [tag1, tag2, tag3]
   published: true
   ---

   # Your Post Title

   Your content starts here...
   ```

   **Required front-matter fields:**
   - `title` - Post title (displayed in listings and post page)
   - `date` - Publication date (YYYY-MM-DD format)
   - `tags` - Array of tags for categorization
   - `published` - Set to `true` to publish, `false` to keep as draft

3. **Write your content** using Markdown syntax below the front-matter

### Building the Blog

Every time you add or edit a blog post, you need to rebuild the static HTML:

```bash
# 1. Activate virtual environment (if not already activated)
source .venv/bin/activate

# 2. Run the build script
python build_blog.py
```

**What the build script does:**
- Reads all `.md` files from `_posts/`
- Skips posts with `published: false`
- Converts Markdown to HTML
- Generates individual post pages in `blog/posts/`
- Creates blog index page at `blog/index.html`
- Builds tag sidebar with post counts

**Expected output:**
```
Building blog...
Generated: blog/posts/2025-11-27-your-post-title.html
Generated: blog/posts/2025-01-15-building-a-simple-blog-system.html
Generated: blog/index.html

Build complete! Generated 2 posts.
```

### Publishing to GitHub Pages

```bash
# 1. Check what was generated
git status

# 2. Add the blog files (both source Markdown and generated HTML)
git add _posts/ blog/

# 3. Commit with a descriptive message
git commit -m "Add new blog post: Your Post Title"

# 4. Push to GitHub
git push origin main
```

GitHub Pages will automatically deploy from the `main` branch.

## Complete Workflow Example

Here's the full workflow from creating a post to publishing it:

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Create new blog post file
touch _posts/2025-11-27-rust-python-interoperability.md

# 3. Edit the file and add front-matter + content
# (use your preferred editor: nano, vim, VS Code, etc.)

# 4. Build the blog
python build_blog.py

# 5. Verify the output
ls blog/posts/

# 6. Commit and push
git add _posts/ blog/
git commit -m "Add blog post: Rust Python Interoperability"
git push origin main
```

## Editing the Main Website

The main landing page (`index.html`) requires **no build step**:

1. Edit `index.html` directly
2. Test locally if needed (see Preview section below)
3. Commit and push

**Common sections to edit:**
- Services section: `index.html` lines ~137-208
- Products section: `index.html` lines ~226-353
- Contact info: `index.html` lines ~385-439

## Previewing the Site Locally

You can preview the entire site using any local web server:

```bash
# Option 1: Python's built-in server
python -m http.server 8000

# Option 2: Using npx (if Node.js is installed)
npx serve .
```

Then open `http://localhost:8000` in your browser.

**Note:** The site uses CDN resources (Tailwind CSS, Google Fonts), so you need an internet connection for proper styling.

## Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'frontmatter'`

**Solution:** Make sure you installed `python-frontmatter` (not just `frontmatter`):
```bash
source .venv/bin/activate
uv add python-frontmatter
```

### Problem: `command not found: python` or `source: no such file`

**Solution:** Activate the virtual environment first:
```bash
source .venv/bin/activate
```

### Problem: Blog post doesn't appear on the website

**Solution:** Check these items:
1. Does the post have `published: true` in the YAML front-matter?
2. Did you run `python build_blog.py` after creating/editing the post?
3. Did you commit and push the generated files in `blog/` directory?
4. Check for errors in the build output

### Problem: Virtual environment doesn't exist

**Solution:** Set it up again:
```bash
uv venv --python 3.14
source .venv/bin/activate
uv add python-frontmatter markdown jinja2
```

## Files and Directories

```
84cs-web-new/
├── index.html              # Main landing page (edit directly)
├── hydrate/
│   └── policy.html         # Hydrate app privacy policy
├── _posts/                 # Blog post source files (Markdown)
│   ├── 2025-01-15-building-a-simple-blog-system.md
│   └── 2025-11-27-rust-python-interoperability.md
├── blog/                   # Generated blog HTML (DO NOT EDIT)
│   ├── index.html          # Blog listing page
│   └── posts/              # Individual post pages
│       ├── 2025-01-15-building-a-simple-blog-system.html
│       └── 2025-11-27-rust-python-interoperability.html
├── build_blog.py           # Blog build script
├── requirements.txt        # Python dependencies (legacy)
├── pyproject.toml          # uv project configuration
├── CNAME                   # Domain configuration (84-cs.com)
└── README.md               # This file
```

## Technology Stack

- **Main Site:** HTML, Tailwind CSS (CDN), vanilla JavaScript
- **Blog Generator:** Python 3.14, Markdown, Jinja2, python-frontmatter
- **Package Manager:** uv
- **Hosting:** GitHub Pages
- **Domain:** 84-cs.com (configured via CNAME)

## Quick Reference

### Blog Workflow (TL;DR)

```bash
source .venv/bin/activate
touch _posts/YYYY-MM-DD-title.md  # Create post with front-matter
python build_blog.py               # Build HTML
git add _posts/ blog/              # Stage changes
git commit -m "Add post: Title"    # Commit
git push origin main               # Deploy
```

### First-Time Setup (TL;DR)

```bash
uv init
uv python pin 3.14
uv venv --python 3.14
source .venv/bin/activate
uv add python-frontmatter markdown jinja2
```
