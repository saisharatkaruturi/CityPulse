"""In-process fixed-window rate limiter.

Limitation: counters live in process memory, so limits are per worker process and reset on
restart. Use a shared store (e.g. Redis) before running multiple API processes.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import RateLimited


@dataclass(frozen=True)
class Limit:
    name: str
    max_requests: int
    window_seconds: int


LOGIN = Limit("login", 10, 60)
REGISTER = Limit("register", 5, 60)
COMPLAINT_CREATE = Limit("complaint_create", 20, 3600)
SEARCH = Limit("search", 60, 60)
UPLOAD = Limit("upload", 30, 3600)
AI_SUGGEST = Limit("ai_suggest", 30, 60)


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[tuple[str, str, int], int] = {}

    def hit(self, limit: Limit, key: str) -> None:
        window = int(time.time() // limit.window_seconds)
        bucket = (limit.name, key, window)
        with self._lock:
            if len(self._counters) > 50_000:
                self._counters = {k: v for k, v in self._counters.items() if k[2] >= window - 1}
            count = self._counters.get(bucket, 0) + 1
            self._counters[bucket] = count
        if count > limit.max_requests:
            raise RateLimited("Too many requests; please retry later")

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()


limiter = RateLimiter()


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def enforce(limit: Limit, request: Request, key: str | None = None) -> None:
    if not get_settings().rate_limit_enabled:
        return
    limiter.hit(limit, key or client_key(request))
