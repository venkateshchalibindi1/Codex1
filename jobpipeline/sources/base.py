from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from jobpipeline.core.models import JobLink, SearchProfile


class SourceAdapter(ABC):
    name: str
    domain: str

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return bool(self.config.get("enabled", False))

    @abstractmethod
    def search(self, profile: SearchProfile) -> list[JobLink]:
        raise NotImplementedError


class StubAdapter(SourceAdapter):
    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        return []
