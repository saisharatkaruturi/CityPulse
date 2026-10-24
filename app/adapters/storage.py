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


_storage: FileStorage | None = None


def get_storage() -> FileStorage:
    global _storage
    if _storage is None:
        from app.core.config import get_settings

        _storage = LocalFileStorage(get_settings().media_root)
    return _storage


def set_storage(storage: FileStorage | None) -> None:
    global _storage
    _storage = storage
