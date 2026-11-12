#!/usr/bin/env python3
"""
Nayfaaro CRM - Branding & White-Label Auditor
Scans the codebase for user-visible occurrences of "frappe" or old branding.
Exits 0 if clean, 1 if user-visible branding violations are found.
"""

import os
import re
import sys
from pathlib import Path

# Terms that should not appear in user-visible strings
FORBIDDEN_PATTERNS = [
    (re.compile(r'\bfrappe\s+crm\b', re.IGNORECASE), "Frappe CRM"),
    (re.compile(r'docs\.frappe\.io', re.IGNORECASE), "Frappe Docs link"),
    (re.compile(r'frappecloud\.com', re.IGNORECASE), "Frappe Cloud link"),
    (re.compile(r'frappemail\.com', re.IGNORECASE), "Frappe Mail domain"),
]

# User-visible string patterns in Vue, HTML, JS, and Python
VISIBLE_STRING_RE = re.compile(
    r"""
    __\(\s*['"]([^'"]+)['"]\s*\)             | # __('translatable text')
    label:\s*['"]([^'"]+)['"]                 | # label: '...'
    title:\s*['"]([^'"]+)['"]                 | # title: '...'
    placeholder:\s*['"]([^'"]+)['"]           | # placeholder: '...'
    description:\s*['"]([^'"]+)['"]           | # description: '...'
    _\(\s*['"]([^'"]+)['"]\s*\)               | # _('python message')
    (?:<title>|<p[^>]*>|<span[^>]*>|<h\d[^>]*>|<div[^>]*>)([^<]+) # HTML element text
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Internal identifiers that are legitimate code and not user-visible
SAFE_CODE_RE = re.compile(
    r"""
    frappe-ui                     |
    frappe\.                      |
    import\s+frappe               |
    from\s+frappe                 |
    @framework                    |
    frappe_mail_site              |
    frappe_providers              |
    frappe_crm                    |
    frappeRequest                 |
    frappe\.call                  |
    frappe\.db                    |
    frappe\.get_doc               |
    frappe\.throw
    """,
    re.VERBOSE,
)

IGNORED_PATHS = [
    "node_modules",
    ".git",
    "dist",
    "crm/locale",  # translation catalog files
    "crm/install.py",  # database translation dictionary seeder
    "tests",
    "license.txt",
    "LICENSE",
]


def should_skip(path: Path) -> bool:
    path_str = str(path)
    return any(ignored in path_str for ignored in IGNORED_PATHS)


def scan_file(file_path: Path):
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                stripped = line.strip()
                # Skip comments
                if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*") or stripped.startswith("*"):
                    continue

                # Skip internal document primary key in JSON files ("name": "...")
                if file_path.suffix == ".json" and stripped.startswith('"name":'):
                    continue

                for pattern, desc in FORBIDDEN_PATTERNS:
                    if pattern.search(line):
                        violations.append((file_path, line_no, desc, stripped))

                # Check for explicit Frappe in visible UI strings
                for match in VISIBLE_STRING_RE.finditer(line):
                    matched_text = next(g for g in match.groups() if g is not None)
                    if re.search(r'\bfrappe\b', matched_text, re.IGNORECASE):
                        if not SAFE_CODE_RE.search(matched_text):
                            violations.append((file_path, line_no, "User-visible text contains 'Frappe'", matched_text.strip()))

    except Exception as e:
        pass
    return violations


def main():
    root_dir = Path(__file__).resolve().parent.parent
    scan_dirs = [root_dir / "frontend" / "src", root_dir / "frontend" / "index.html", root_dir / "crm"]

    all_violations = []
    files_count = 0

    print("=" * 60)
    print(" Nayfaaro CRM — Automated White-Labeling & Branding Audit")
    print("=" * 60)

    for target in scan_dirs:
        if target.is_file():
            files_count += 1
            all_violations.extend(scan_file(target))
        elif target.is_dir():
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith((".vue", ".js", ".ts", ".html", ".py", ".json")):
                        fpath = Path(root) / file
                        if not should_skip(fpath):
                            files_count += 1
                            all_violations.extend(scan_file(fpath))

    print(f"Scanned {files_count} files across frontend and backend.\n")

    if not all_violations:
        print("\033[92m✔ SUCCESS: 0 branding violations found! All user-visible surfaces are clean Nayfaaro branding.\033[0m\n")
        return 0
    else:
        print(f"\033[91m✘ FOUND {len(all_violations)} POTENTIAL BRANDING VIOLATIONS:\033[0m\n")
        for fpath, lno, reason, snippet in all_violations:
            rel = fpath.relative_to(root_dir)
            print(f"  • {rel}:{lno} [{reason}]")
            print(f"    Line: {snippet[:100]}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
