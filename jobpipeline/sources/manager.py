from __future__ import annotations

from urllib.parse import urlparse

from jobpipeline.core.models import JobLink, SearchProfile
from jobpipeline.sources.adapters import apply_time_window, build_adapters


class SourceManager:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.adapters = build_adapters(cfg.get("sources", {}))

    def search(self, profile: SearchProfile) -> list[JobLink]:
        include = set(self.cfg.get("include_domains", []))
        exclude = set(self.cfg.get("exclude_domains", []))
        links: list[JobLink] = []
        for adapter in self.adapters:
            try:
                links.extend(adapter.search(profile))
            except Exception:
                continue
        out: list[JobLink] = []
        for link in apply_time_window(links, profile):
            domain = urlparse(link.job_url).netloc
            if exclude and any(d in domain for d in exclude):
                continue
            if include and not any(d in domain for d in include):
                continue
            out.append(link)
        return out

    def h1b_mode_links(self, profile: SearchProfile) -> list[JobLink]:
        links: list[JobLink] = []
        source_by_name = {a.name: a for a in self.adapters}
        for entry in self.cfg.get("h1b_employers", []):
            ats = entry.get("ats")
            slug = entry.get("board_slug")
            if ats == "greenhouse" and "greenhouse_api" in source_by_name:
                source_by_name["greenhouse_api"].config["boards"] = [slug]
                links.extend(source_by_name["greenhouse_api"].search(profile))
            elif ats == "lever" and "lever_api" in source_by_name:
                source_by_name["lever_api"].config["companies"] = [slug]
                links.extend(source_by_name["lever_api"].search(profile))
        return links
