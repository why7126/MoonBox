from pathlib import Path

required = [
    "MINIO_BUCKET",
    "OBJECT_STORAGE_DEPLOYMENT_MODE",
    "OBJECT_STORAGE_KEY_PATTERN",
    "OBJECT_STORAGE_PREFIX_IMAGES_ORIGINAL",
    "OBJECT_STORAGE_PREFIX_IMAGES_THUMBNAILS",
    "OBJECT_STORAGE_PREFIX_IMAGES_PROCESSED",
    "OBJECT_STORAGE_PREFIX_DOCUMENTS_SOURCE",
    "OBJECT_STORAGE_PREFIX_DOCUMENTS_PREVIEW",
    "OBJECT_STORAGE_PREFIX_DOCUMENTS_PROCESSED",
    "OBJECT_STORAGE_PREFIX_IMPORTS_SOURCE",
    "OBJECT_STORAGE_PREFIX_IMPORTS_PROCESSED",
    "OBJECT_STORAGE_PREFIX_EXPORTS_RESULT",
    "OBJECT_STORAGE_PREFIX_TMP_UPLOADS",
    "HOST_PORT_BACKEND",
    "HOST_PORT_WEB",
    "HOST_PORT_MINTLIFY_DOCS",
    "DATABASE_DEPLOYMENT_MODE",
]

content = Path(".env.example").read_text(encoding="utf-8")
missing = [key for key in required if key not in content]

if missing:
    raise SystemExit(f"Missing env keys in .env.example: {', '.join(missing)}")

print(".env.example check passed")
