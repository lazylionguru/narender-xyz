"""
Patch all existing blog posts to add onerror handler to figure images.
Run once from ~/narender-xyz: python fix_figures.py
"""
from pathlib import Path
import re

blog_dir = Path(__file__).parent / "blog"
posts = list(blog_dir.glob("*/index.html"))
fixed = 0

for post in posts:
    content = post.read_text(encoding="utf-8")
    if 'post-figure' not in content:
        continue
    # Add onerror if not already present
    if 'onerror' not in content:
        new_content = re.sub(
            r'(<img\s[^>]*class="[^"]*"[^>]*)(loading="lazy")',
            r'\1\2 onerror="this.classList.add(\'hidden\')"',
            content
        )
        # Broader fallback for any img inside post-figure
        new_content = re.sub(
            r'(class="post-figure">\s*<img\b(?![^>]*onerror)[^>]*)(>)',
            lambda m: m.group(1) + ' onerror="this.classList.add(\'hidden\')"' + m.group(2),
            new_content,
            flags=re.DOTALL
        )
        if new_content != content:
            post.write_text(new_content, encoding="utf-8")
            print(f"  Patched: {post.parent.name}")
            fixed += 1

print(f"\nDone. Fixed {fixed} post(s).")
