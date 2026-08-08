#!/usr/bin/env python3
"""Validate the PM Harness template directory structure."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "project.yaml",
    "DOCUMENT_METADATA_INDEX.md",
    ".gitignore",
    ".dockerignore",
    ".env.example",
    "pytest.ini",
    "rules/directory-structure.md",
    "rules/issues-lifecycle.md",
    "rules/iterations-lifecycle.md",
    "rules/global.md",
    "rules/testing.md",
    "issues/requirements/_registry.yaml",
    "issues/bugs/_registry.yaml",
    "docs/README.md",
    "docs/00-product-overview.md",
    "docs/01-architecture.md",
    "docs/02-deployment.md",
    "docs/03-api-index.md",
    "docs/04-database-design.md",
    "docs/05-compatibility-matrix.md",
    "docs/knowledge-base/README.md",
    "docs/spec-logs/README.md",
    "openspec/project.md",
    "openspec/config.yaml",
    "openspec/testing-mapping.md",
    "releases/README.md",
    "releases/mint.json",
    "releases/templates/release.json",
    "releases/templates/announcement.mdx",
    "mintlify/README.md",
    "mintlify/mint.json",
    "mintlify/site-manifest.json",
    "deploy/README.md",
    "deploy/local/README.md",
    "deploy/local/compose.yml",
    "deploy/prod/README.md",
    "deploy/prod/compose.s3-mysql.yml",
    "deploy/scripts/up.sh",
    "deploy/scripts/down.sh",
    "deploy/scripts/validate-env.py",
    "deploy/scripts/docs-site-static-server.mjs",
    "docker-compose.yml",
    "scripts/promote-issue-stage.py",
    "scripts/promote-issues-for-archive.py",
    "scripts/add-sprint-scope-item.py",
    "scripts/archive_evidence.py",
    "scripts/archived_path_residuals.py",
    "scripts/check-sprint-close-stale-scan.py",
    "scripts/check-archived-path-residuals.py",
    "scripts/generate-sprint-fact-sheet.py",
    "scripts/sprint_change_batches.py",
    "scripts/sprint_close_stale_scan.py",
    "scripts/validate-archive-evidence.py",
    "scripts/validate-directory-structure.py",
    "scripts/validate-env-ignore-policy.py",
    "scripts/validate-sprint-archive-readiness.py",
    "scripts/validate-sprint-scope.py",
    "scripts/validate-release.py",
    "scripts/generate-mintlify-docs.py",
    "scripts/validate-mintlify-docs.py",
    "scripts/validate-openspec-language.py",
    "scripts/validate-image-build.py",
    "scripts/build-images.sh",
    "scripts/build-images.env.example",
    "src/shared/product-version.ts",
]

REQUIRED_DIRS = [
    ".agents",
    "rules",
    "docs",
    "docs/standards",
    "docs/knowledge-base",
    "docs/knowledge-base/best-practices",
    "docs/knowledge-base/incidents",
    "docs/knowledge-base/sprints",
    "docs/spec-logs",
    "compatibility",
    "compatibility/database",
    "compatibility/devices",
    "compatibility/object-storage",
    "openspec",
    "openspec/specs",
    "openspec/changes",
    "openspec/archive",
    "issues",
    "issues/requirements",
    "issues/requirements/plan",
    "issues/requirements/review",
    "issues/requirements/archive",
    "issues/bugs",
    "issues/bugs/plan",
    "issues/bugs/review",
    "issues/bugs/archive",
    "iterations",
    "iterations/change",
    "iterations/archive",
    "releases",
    "releases/templates",
    "mintlify",
    "mintlify/docs",
    "mintlify/docs/latest",
    "mintlify/releases",
    "mintlify/assets",
    "mintlify/assets/screenshots",
    "scripts",
    "src",
    "src/backend",
    "src/web",
    "src/shared",
    "src/sdk",
    "src/infrastructure",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/integration/api",
    "tests/e2e",
    "tests/compatibility",
    "data",
    "models",
    "deploy",
    "deploy/local",
    "deploy/prod",
    "deploy/scripts",
]

ALLOWED_ROOT_FILES = {
    "AGENTS.md",
    "README.md",
    ".gitignore",
    ".dockerignore",
    ".env.example",
    ".coveragerc",
    "docker-compose.yml",
    "project.yaml",
    "DOCUMENT_METADATA_INDEX.md",
    "pytest.ini",
}

ALLOWED_ROOT_DIRS = {
    "rules",
    "docs",
    "openspec",
    "issues",
    "iterations",
    "releases",
    "compatibility",
    ".agents",
    "src",
    "tests",
    "scripts",
    "data",
    "models",
    "deploy",
    "mintlify",
}

errors = []

FORBIDDEN_PATHS = [
    "openspec/changes/archive",
]

IGNORED_ROOT_NAMES = {
    ".DS_Store",
    ".env",
    ".env.local",
    ".env.mysql",
    ".pytest_cache",
    ".venv",
}


def is_ignored_local_env_file(path: Path) -> bool:
    """Allow gitignored local env overlays to exist without changing governance roots."""
    return path.is_file() and path.name.startswith(".env.") and path.name != ".env.example"


for item in REQUIRED_PATHS:
    if not (ROOT / item).exists():
        errors.append(f"缺少必需路径: {item}")

for item in REQUIRED_DIRS:
    if not (ROOT / item).is_dir():
        errors.append(f"缺少必需目录: {item}")

for item in FORBIDDEN_PATHS:
    if (ROOT / item).exists():
        errors.append(f"禁止使用旧 OpenSpec 归档路径: {item}，请改用 openspec/archive")

for child in ROOT.iterdir():
    if child.name in IGNORED_ROOT_NAMES:
        continue
    if is_ignored_local_env_file(child):
        continue
    if child.name.startswith(".git"):
        continue
    if child.is_file() and child.name not in ALLOWED_ROOT_FILES:
        errors.append(f"根目录存在未登记文件: {child.name}")
    if child.is_dir() and child.name not in ALLOWED_ROOT_DIRS:
        errors.append(f"根目录存在未登记目录: {child.name}")

if errors:
    print("目录结构校验失败：")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)

print("目录结构校验通过。")
