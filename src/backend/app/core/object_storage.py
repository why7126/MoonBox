from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class ObjectStorageError(RuntimeError):
    """Raised when object storage cannot persist or read an object."""


@dataclass(frozen=True)
class StoredObject:
    key: str
    content_type: str
    data: bytes


class ObjectStorage:
    def __init__(self) -> None:
        self._client = Minio(
            settings.object_storage_endpoint,
            access_key=settings.object_storage_access_key,
            secret_key=settings.object_storage_secret_key,
            secure=settings.object_storage_secure,
        )

    @property
    def bucket(self) -> str:
        return settings.object_storage_bucket

    def ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
        except Exception as exc:
            raise ObjectStorageError("对象存储桶初始化失败。") from exc

    def put(self, key: str, content: bytes, content_type: str) -> None:
        self.ensure_bucket()
        try:
            self._client.put_object(
                self.bucket,
                key,
                BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
        except Exception as exc:
            raise ObjectStorageError("对象上传失败。") from exc

    def get(self, key: str) -> StoredObject:
        try:
            response = self._client.get_object(self.bucket, key)
            try:
                content_type = response.headers.get("content-type") or "application/octet-stream"
                data = response.read()
            finally:
                response.close()
                response.release_conn()
        except Exception as exc:
            if isinstance(exc, S3Error) and exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                raise FileNotFoundError("头像不存在。") from exc
            raise ObjectStorageError("对象读取失败。") from exc
        return StoredObject(key=key, content_type=content_type, data=data)


def get_object_storage() -> ObjectStorage:
    return ObjectStorage()
