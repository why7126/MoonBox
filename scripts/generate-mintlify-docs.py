#!/usr/bin/env python3
"""Generate MoonBox Mintlify navigation and release projections."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MINTLIFY_DIR = ROOT / "mintlify"
RELEASES_DIR = ROOT / "releases"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def page_id(path: Path) -> str:
    return str(path.relative_to(MINTLIFY_DIR).with_suffix("")).replace("\\", "/")


def discover_pages(version: str) -> list[str]:
    docs_root = MINTLIFY_DIR / "docs" / version
    if not docs_root.exists():
        raise SystemExit(f"缺少产品手册目录: {docs_root}")
    preferred = ["overview", "admin", "deployment", "faq"]
    pages: list[str] = []
    for stem in preferred:
        path = docs_root / f"{stem}.mdx"
        if path.exists():
            pages.append(page_id(path))
    for path in sorted(docs_root.rglob("*.mdx")):
        pid = page_id(path)
        if pid not in pages:
            pages.append(pid)
    return pages


def sync_release_announcements() -> list[str]:
    pages: list[str] = []
    if not RELEASES_DIR.exists():
        return pages
    for release_dir in sorted(RELEASES_DIR.iterdir()):
        if not release_dir.is_dir() or not release_dir.name.startswith("v"):
            continue
        src = release_dir / "announcement.mdx"
        if not src.exists():
            continue
        target = MINTLIFY_DIR / "releases" / release_dir.name / "announcement.mdx"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        pages.append(page_id(target))
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Mintlify docs metadata")
    parser.add_argument("--version", default="latest", help="Mintlify docs version to expose as current")
    args = parser.parse_args()

    (MINTLIFY_DIR / "assets" / "screenshots").mkdir(parents=True, exist_ok=True)
    (MINTLIFY_DIR / "releases").mkdir(parents=True, exist_ok=True)

    current_pages = discover_pages(args.version)
    release_pages = sync_release_announcements()
    navigation: list[dict[str, Any]] = [
        {
            "group": "当前版本",
            "pages": current_pages,
        }
    ]
    if release_pages:
        navigation.append({"group": "发布公告", "pages": release_pages})
    else:
        navigation.append({"group": "发布公告", "pages": []})

    write_json(
        MINTLIFY_DIR / "mint.json",
        {
            "$schema": "https://mintlify.com/schema.json",
            "name": "MoonBox 产品手册",
            "navigation": navigation,
        },
    )
    write_json(
        MINTLIFY_DIR / "site-manifest.json",
        {
            "updated_at": now_text(),
            "latest_version": args.version,
            "versions": sorted(path.name for path in (MINTLIFY_DIR / "docs").iterdir() if path.is_dir()),
            "assets": sorted(str(path.relative_to(MINTLIFY_DIR)).replace("\\", "/") for path in (MINTLIFY_DIR / "assets").rglob("*") if path.is_file() and path.name != ".gitkeep"),
            "projections": [
                {
                    "status": "synced",
                    "source_docs": [
                        "docs/00-product-overview.md",
                        "docs/02-deployment.md",
                        "releases/**/announcement.mdx",
                    ],
                    "target_site_root": f"mintlify/docs/{args.version}",
                    "release_pages": release_pages,
                    "synced_at": now_text(),
                    "mode": "metadata-and-release-copy",
                    "manual_overrides": [],
                }
            ],
        },
    )
    print(f"Mintlify 产品手册元数据已生成：{MINTLIFY_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

