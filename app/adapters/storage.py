"""Private file storage behind an interface. Local filesystem implementation.

Storage keys are server-generated opaque names; client filenames are never used as paths.
"""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Protocol


class FileStorage(Protocol):
    def put(self, data: bytes, extension: str) -> str: ...

    def get(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...


class LocalFileStorage:
    def __init__(self, root: str) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if not key or "/" in key or "\\" in key or ".." in key:
            raise ValueError("invalid storage key")
        path = (self.root / key).resolve()
        if path.parent != self.root:
            raise ValueError("invalid storage key")
        return path

    def put(self, data: bytes, extension: str) -> str:
        key = f"{secrets.token_hex(16)}.{extension}"
        self._path(key).write_bytes(data)
        return key

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class VercelBlobStorage:
    """Vercel Blob (object storage) over its HTTP API.

    Use a *private* Blob store: every read then needs the store token, so a leaked blob URL alone
    exposes nothing. Blobs get unguessable 128-bit names; the blob URL is the storage key and stays
    server-side. Media is served to users only through the authorised /api/media endpoint.
    """

    api_url = "https://blob.vercel-storage.com"
    api_version = "11"

    def __init__(self, token: str, timeout: float = 15.0, access: str = "private") -> None:
        if not token:
            raise ValueError("BLOB_READ_WRITE_TOKEN is required for Vercel Blob storage")
        self._token = token
        self._timeout = timeout
        self._access = access

    def _headers(self) -> dict[str, str]:
        return {"authorization": f"Bearer {self._token}", "x-api-version": self.api_version}

    def put(self, data: bytes, extension: str) -> str:
        import httpx

        pathname = f"media/{secrets.token_hex(16)}.{extension}"
        content_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                        "webp": "image/webp"}.get(extension, "application/octet-stream")
        resp = httpx.put(f"{self.api_url}/?pathname={pathname}", content=data, timeout=self._timeout,
                         headers={**self._headers(), "x-content-type": content_type,
                                  "x-add-random-suffix": "0", "x-vercel-blob-access": self._access})
        resp.raise_for_status()
        url = resp.json()["url"]
        if not isinstance(url, str) or not url.startswith("https://"):
            raise RuntimeError("unexpected Vercel Blob response")
        return url

    def get(self, key: str) -> bytes:
        import httpx

        self._check(key)
        resp = httpx.get(key, timeout=self._timeout, headers={"authorization": f"Bearer {self._token}"})
        if resp.status_code == 404:
            raise FileNotFoundError(key)
        resp.raise_for_status()
        return resp.content

    def delete(self, key: str) -> None:
        import httpx

        self._check(key)
        resp = httpx.post(f"{self.api_url}/delete", json={"urls": [key]}, timeout=self._timeout,
                          headers=self._headers())
        resp.raise_for_status()

    @staticmethod
    def _check(key: str) -> None:
        # Only ever fetch from Vercel Blob hosts, so a corrupted key can't turn into an SSRF.
        from urllib.parse import urlparse

        parsed = urlparse(key)
        if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".blob.vercel-storage.com"):
            raise ValueError("invalid storage key")


_storage: FileStorage | None = None


def get_storage() -> FileStorage:
    global _storage
    if _storage is None:
        from app.core.config import get_settings

        settings = get_settings()
        if settings.effective_storage_backend == "vercel_blob":
            _storage = VercelBlobStorage(settings.blob_read_write_token, settings.external_call_timeout_seconds * 3,
                                        settings.blob_access)
        else:
            _storage = LocalFileStorage(settings.media_root)
    return _storage


def set_storage(storage: FileStorage | None) -> None:
    global _storage
    _storage = storage
