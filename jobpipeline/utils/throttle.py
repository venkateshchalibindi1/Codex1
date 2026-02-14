from __future__ import annotations

import time
from collections import defaultdict


class DomainThrottle:
    def __init__(self, default_delay_seconds: float = 0.5) -> None:
        self.default_delay_seconds = default_delay_seconds
        self._last_hit: dict[str, float] = defaultdict(float)

    def wait(self, domain: str) -> None:
        now = time.monotonic()
        elapsed = now - self._last_hit[domain]
        if elapsed < self.default_delay_seconds:
            time.sleep(self.default_delay_seconds - elapsed)
        self._last_hit[domain] = time.monotonic()
