#!/usr/bin/env python3
"""
Repository analytics script.
Generates a Markdown report with:
- Total Python LOC
- Total LOC (all files)
- LOC per top-level directory (Python only)
- File counts by extension
- Overall file count
- One-level repo layout
- Commit hash and timestamp
- Excluded paths
"""

import subprocess
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Directories to ignore when counting
EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "__pycache__",
    "litime_ble.egg-info",
    "repo_stats",
}


def count_loc(file_path: Path) -> int:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def git_commit_hash(repo_root: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def main():
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = Path(__file__).resolve().parent
    script_name = Path(__file__).stem
    out_dir = scripts_dir / script_name
    out_dir.mkdir(exist_ok=True)

    # Collect stats
    python_loc = 0
    total_loc = 0
    loc_by_dir = defaultdict(int)
    file_counts = Counter()
    total_files = 0

    for path in repo_root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_file():
            total_files += 1
            ext = path.suffix.lower() or "NOEXT"
            file_counts[ext] += 1

            loc = count_loc(path)
            total_loc += loc

            if ext == ".py":
                python_loc += loc
                parts = path.relative_to(repo_root).parts
                if parts:
                    top = parts[0]
                    loc_by_dir[top] += loc

    # Build tree (1 level deep)
    layout_lines = []
    for item in sorted(repo_root.iterdir()):
        if any(part in EXCLUDE_DIRS for part in item.parts):
            continue
        if item.is_dir():
            layout_lines.append(f"- {item.name}/")
            for sub in sorted(item.iterdir()):
                if any(part in EXCLUDE_DIRS for part in sub.parts):
                    continue
                if sub.is_dir():
                    layout_lines.append(f"  - {sub.name}/")
                else:
                    layout_lines.append(f"  - {sub.name}")
        else:
            layout_lines.append(f"- {item.name}")

    # Metadata
    commit = git_commit_hash(repo_root)
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Markdown report
    report = f"""# Repository Stats

- **Commit**: {commit}
- **Generated**: {timestamp}

- **Total Python LOC**: {python_loc}
- **Total LOC (all files)**: {total_loc}
- **Total files**: {total_files}

## LOC by Top-Level Directory (Python only)

"""
    for d, loc in sorted(loc_by_dir.items(), key=lambda x: x[1], reverse=True):
        report += f"- {d}: {loc} LOC\n"

    report += "\n## File Counts by Extension\n\n"
    for ext, count in file_counts.most_common():
        report += f"- {ext}: {count}\n"

    report += "\n## Top-Level Layout\n\n"
    report += "\n".join(layout_lines)

    report += "\n\n## Excluded Paths\n\n"
    for d in sorted(EXCLUDE_DIRS):
        report += f"- {d}\n"

    out_path = out_dir / f"{script_name}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote report to {out_path}")

    # Also write to docs/ with Jekyll front matter
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        # Add Jekyll front matter to the report
        jekyll_report = f"""---
title: "Repository Statistics"
layout: single
permalink: /repo-stats/
toc: true
---

{report}"""

        docs_path = docs_dir / "repo-stats.md"
        docs_path.write_text(jekyll_report, encoding="utf-8")
        print(f"Published to docs: {docs_path}")

        # Update docs index.md to include link
        update_docs_index(docs_dir / "index.md")
    else:
        print("Warning: docs/ directory not found, skipping docs publication")


def update_docs_index(index_path: Path):
    """Add repo stats link to docs index if not already present."""
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")

    # Check if repo-stats link already exists
    if "repo-stats" in content or "Repository Statistics" in content:
        print("Repo stats link already exists in docs index")
        return

    # Find the Contents section and add our link
    lines = content.split("\n")
    new_lines = []
    added = False

    for line in lines:
        new_lines.append(line)
        # Add after the existing links in the Contents section
        if "- [Reference implementation (JavaScript)]" in line and not added:
            new_lines.append(
                '- [Repository statistics]({{ "/repo-stats/" | relative_url }})'
            )
            added = True

    if added:
        index_path.write_text("\n".join(new_lines), encoding="utf-8")
        print("Added repo stats link to docs index")
    else:
        print("Could not find insertion point in docs index")


if __name__ == "__main__":
    main()
