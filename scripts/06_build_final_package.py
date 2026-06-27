#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_build_final_package.py — Zip the repository (code + reports + docs) as a GitHub evidence package.

Excludes the source PDF and large rendered images (per .gitignore policy / data sensitivity).
Includes: scripts, docs, README, requirements, tests, issue registry, audit reports, evidence crops.

Usage:
    python scripts/06_build_final_package.py
Output: output/final_delivery/GitHub_Repository_Package.zip
"""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

INCLUDE_DIRS = ["scripts", "docs", "tests"]
INCLUDE_FILES = ["README.md", "LICENSE", ".gitignore", "requirements.txt"]
INCLUDE_GLOBS = [
    ("data/issue_registry", (".csv", ".md", ".json")),
    ("output/audit_reports", (".xlsx", ".md")),
    ("output/audit_reports/evidence", (".png",)),
    ("data", (".json",)),  # baseline_lock.json, render_manifest.json
]


def main():
    out_dir = os.path.join(ROOT, "output", "final_delivery")
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, "GitHub_Repository_Package.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for d in INCLUDE_DIRS:
            for root, _, files in os.walk(os.path.join(ROOT, d)):
                for f in files:
                    if f.endswith(".pyc"):
                        continue
                    p = os.path.join(root, f)
                    z.write(p, os.path.relpath(p, ROOT))
        for f in INCLUDE_FILES:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                z.write(p, f)
        for folder, exts in INCLUDE_GLOBS:
            ap = os.path.join(ROOT, folder)
            if not os.path.isdir(ap):
                continue
            for f in os.listdir(ap):
                if f.endswith(exts):
                    p = os.path.join(ap, f)
                    z.write(p, os.path.relpath(p, ROOT))
    print("Package written:", zpath, f"({os.path.getsize(zpath)} bytes)")


if __name__ == "__main__":
    main()
