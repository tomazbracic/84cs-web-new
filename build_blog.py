#!/usr/bin/env python3
"""
Blog builder for 84-CS website
Converts Markdown posts to static HTML pages
"""

import os
import re
from datetime import datetime
from pathlib import Path
import frontmatter
import markdown
from jinja2 import Template
from collections import defaultdict

# Directories
POSTS_DIR = Path("_posts")
OUTPUT_DIR = Path("blog")
POSTS_OUTPUT_DIR = OUTPUT_DIR / "posts"

# Templates
BLOG_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog | 84-CS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
    </style>
</head>
<body class="bg-white">
    <header class="fixed top-0 left-0 right-0 bg-white z-50 border-b border-gray-100">
        <div class="container mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-xl font-mono font-bold">84-CS</a>
            <nav>
                <ul class="flex space-x-8">
                    <li><a href="/" class="text-gray-600 hover:text-gray-900">Home</a></li>
                    <li><a href="/blog" class="text-blue-600 font-semibold">Blog</a></li>
                    <li><a href="/#contact" class="text-gray-600 hover:text-gray-900">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="h-20"></div>

    <div class="container mx-auto px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <h1 class="font-mono text-4xl font-bold mb-12">Blog</h1>

            <div class="flex gap-8">
                <!-- Blog Posts (Left Side) -->
                <div class="flex-grow">
                    {% if posts %}
                        {% for post in posts %}
                        <article class="mb-8 pb-8 border-b border-gray-200">
                            <h2 class="font-mono text-2xl font-bold mb-2">
                                <a href="/blog/posts/{{ post.slug }}.html" class="text-gray-900 hover:text-blue-600">
                                    {{ post.title }}
                                </a>
                            </h2>
                            <div class="text-sm text-gray-500 mb-4">{{ post.date }}</div>
                            <div class="flex gap-2 mb-4">
                                {% for tag in post.tags %}
                                <span class="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm">{{ tag }}</span>
                                {% endfor %}
                            </div>
                            <p class="text-gray-600">{{ post.excerpt }}</p>
                            <a href="/blog/posts/{{ post.slug }}.html" class="text-blue-600 hover:underline text-sm mt-2 inline-block">
                                Read more →
                            </a>
                        </article>
                        {% endfor %}
                    {% else %}
                        <p class="text-gray-600">No blog posts yet.</p>
                    {% endif %}
                </div>

                <!-- Tags Sidebar (Right Side) -->
                <aside class="w-64 flex-shrink-0">
                    <div class="bg-gray-50 p-6 rounded-lg sticky top-24">
                        <h3 class="font-mono text-lg font-bold mb-4">Tags</h3>
                        <div class="flex flex-wrap gap-2">
                            {% for tag, count in tags.items() %}
                            <span class="bg-white border border-gray-200 px-3 py-1 rounded-full text-sm">
                                {{ tag }} ({{ count }})
                            </span>
                            {% endfor %}
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    </div>

    <footer class="py-8 border-t mt-16">
        <div class="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
            <div class="text-sm text-gray-600 mb-4 md:mb-0">
                <span class="font-mono font-bold">84-CS</span> | Software Development & Infrastructure
            </div>
            <div class="text-sm text-gray-600">
                &copy; 2025 84-CS. All rights reserved.
            </div>
        </div>
    </footer>
</body>
</html>
"""

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | 84-CS Blog</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .prose { max-width: 65ch; }
        .prose h1 { font-family: 'JetBrains Mono', monospace; font-size: 2.25rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem; }
        .prose h2 { font-family: 'JetBrains Mono', monospace; font-size: 1.875rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem; }
        .prose h3 { font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 0.75rem; }
        .prose p { margin-bottom: 1rem; line-height: 1.75; color: #374151; }
        .prose pre { background-color: #1f2937; color: #f3f4f6; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1rem; }
        .prose code { background-color: #f3f4f6; padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-size: 0.875rem; }
        .prose pre code { background-color: transparent; padding: 0; }
        .prose ul { list-style-type: disc; margin-left: 1.5rem; margin-bottom: 1rem; }
        .prose ol { list-style-type: decimal; margin-left: 1.5rem; margin-bottom: 1rem; }
        .prose li { margin-bottom: 0.5rem; }
        .prose a { color: #3b82f6; text-decoration: underline; }
        .prose blockquote { border-left: 4px solid #3b82f6; padding-left: 1rem; color: #6b7280; margin-bottom: 1rem; }
    </style>
</head>
<body class="bg-white">
    <header class="fixed top-0 left-0 right-0 bg-white z-50 border-b border-gray-100">
        <div class="container mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-xl font-mono font-bold">84-CS</a>
            <nav>
                <ul class="flex space-x-8">
                    <li><a href="/" class="text-gray-600 hover:text-gray-900">Home</a></li>
                    <li><a href="/blog" class="text-blue-600 font-semibold">Blog</a></li>
                    <li><a href="/#contact" class="text-gray-600 hover:text-gray-900">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="h-20"></div>

    <article class="container mx-auto px-4 py-12">
        <div class="max-w-4xl mx-auto">
            <div class="mb-8">
                <a href="/blog" class="text-blue-600 hover:underline text-sm">← Back to Blog</a>
            </div>

            <h1 class="font-mono text-4xl font-bold mb-4">{{ title }}</h1>
            <div class="text-gray-500 mb-6">{{ date }}</div>

            <div class="flex gap-2 mb-8">
                {% for tag in tags %}
                <span class="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm">{{ tag }}</span>
                {% endfor %}
            </div>

            <div class="prose">
                {{ content | safe }}
            </div>

            <div class="mt-12 pt-8 border-t border-gray-200">
                <a href="/blog" class="text-blue-600 hover:underline">← Back to Blog</a>
            </div>
        </div>
    </article>

    <footer class="py-8 border-t mt-16">
        <div class="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
            <div class="text-sm text-gray-600 mb-4 md:mb-0">
                <span class="font-mono font-bold">84-CS</span> | Software Development & Infrastructure
            </div>
            <div class="text-sm text-gray-600">
                &copy; 2025 84-CS. All rights reserved.
            </div>
        </div>
    </footer>
</body>
</html>
"""


def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def extract_excerpt(content, max_length=200):
    """Extract first paragraph or N characters as excerpt"""
    # Remove markdown formatting
    plain = re.sub(r'[#*`\[\]]', '', content)
    # Get first paragraph
    first_para = plain.split('\n\n')[0]
    # Truncate if too long
    if len(first_para) > max_length:
        return first_para[:max_length].rsplit(' ', 1)[0] + '...'
    return first_para


def build_blog():
    """Main build function"""
    print("Building blog...")

    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    POSTS_OUTPUT_DIR.mkdir(exist_ok=True)

    # Check if _posts directory exists
    if not POSTS_DIR.exists():
        print(f"Creating {POSTS_DIR} directory...")
        POSTS_DIR.mkdir(exist_ok=True)
        print("No posts found. Add .md files to _posts/ directory.")
        return

    # Load all posts
    posts = []
    tags_count = defaultdict(int)

    for md_file in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        post = frontmatter.load(md_file)

        # Skip unpublished posts
        if not post.get('published', False):
            print(f"Skipping unpublished: {md_file.name}")
            continue

        # Extract metadata
        title = post.get('title', md_file.stem)
        date = post.get('date', datetime.now())
        tags = post.get('tags', [])

        # Convert date to string if datetime
        if isinstance(date, datetime):
            date_str = date.strftime('%B %d, %Y')
        else:
            date_str = str(date)

        # Generate slug from filename or title
        slug = md_file.stem

        # Convert markdown to HTML
        html_content = markdown.markdown(
            post.content,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )

        # Extract excerpt
        excerpt = extract_excerpt(post.content)

        # Count tags
        for tag in tags:
            tags_count[tag] += 1

        # Render post page
        post_html = Template(POST_TEMPLATE).render(
            title=title,
            date=date_str,
            tags=tags,
            content=html_content
        )

        # Write post HTML
        post_output = POSTS_OUTPUT_DIR / f"{slug}.html"
        post_output.write_text(post_html)
        print(f"Generated: {post_output}")

        # Add to posts list for index
        posts.append({
            'title': title,
            'date': date_str,
            'tags': tags,
            'slug': slug,
            'excerpt': excerpt
        })

    # Render blog index
    index_html = Template(BLOG_INDEX_TEMPLATE).render(
        posts=posts,
        tags=dict(sorted(tags_count.items()))
    )

    index_output = OUTPUT_DIR / "index.html"
    index_output.write_text(index_html)
    print(f"Generated: {index_output}")

    print(f"\nBuild complete! Generated {len(posts)} posts.")


if __name__ == "__main__":
    build_blog()
