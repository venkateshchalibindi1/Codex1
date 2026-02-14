from __future__ import annotations

from datetime import datetime, timedelta
from email import policy
from email.parser import BytesParser
from typing import Any
import json


from jobpipeline.core.models import JobLink, SearchProfile
from jobpipeline.sources.base import SourceAdapter, StubAdapter


class JsonApiAdapter(SourceAdapter):
    endpoint: str = ""

    def fetch_json(self) -> Any:
        import httpx
        with httpx.Client(timeout=15) as client:
            resp = client.get(self.endpoint)
            resp.raise_for_status()
            return resp.json()


class RemoteOkAdapter(JsonApiAdapter):
    name, domain = "remoteok_api", "remoteok.com"
    endpoint = "https://remoteok.com/api"

    @staticmethod
    def parse(data: list[dict[str, Any]]) -> list[JobLink]:
        links: list[JobLink] = []
        for item in data:
            url = item.get("url")
            if not url:
                continue
            links.append(JobLink(job_url=url, source_name="Remote OK API", source_domain="remoteok.com", snippet_meta=item))
        return links

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        try:
            return self.parse(self.fetch_json())
        except Exception:
            return []


class RemotiveAdapter(JsonApiAdapter):
    name, domain = "remotive_api", "remotive.com"
    endpoint = "https://remotive.com/api/remote-jobs"

    @staticmethod
    def parse(data: dict[str, Any]) -> list[JobLink]:
        return [
            JobLink(j["url"], "Remotive API", "remotive.com", j)
            for j in data.get("jobs", [])
            if j.get("url")
        ]

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        try:
            return self.parse(self.fetch_json())
        except Exception:
            return []


class ArbeitnowAdapter(JsonApiAdapter):
    name, domain = "arbeitnow_api", "arbeitnow.com"
    endpoint = "https://www.arbeitnow.com/api/job-board-api"

    @staticmethod
    def parse(data: dict[str, Any]) -> list[JobLink]:
        return [
            JobLink(j["url"], "Arbeitnow API", "arbeitnow.com", j)
            for j in data.get("data", [])
            if j.get("url")
        ]

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        try:
            return self.parse(self.fetch_json())
        except Exception:
            return []


class GreenhouseApiAdapter(JsonApiAdapter):
    name, domain = "greenhouse_api", "boards.greenhouse.io"

    @staticmethod
    def parse(data: dict[str, Any], board: str) -> list[JobLink]:
        links: list[JobLink] = []
        for job in data.get("jobs", []):
            absolute_url = job.get("absolute_url")
            if absolute_url:
                links.append(JobLink(absolute_url, f"Greenhouse:{board}", "greenhouse.io", job))
        return links

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        out: list[JobLink] = []
        for board in self.config.get("boards", []):
            try:
                self.endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
                out.extend(self.parse(self.fetch_json(), board))
            except Exception:
                continue
        return out


class LeverApiAdapter(JsonApiAdapter):
    name, domain = "lever_api", "api.lever.co"

    @staticmethod
    def parse(data: list[dict[str, Any]], company: str) -> list[JobLink]:
        links: list[JobLink] = []
        for job in data:
            url = job.get("hostedUrl") or job.get("applyUrl")
            if url:
                links.append(JobLink(url, f"Lever:{company}", "lever.co", job))
        return links

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        out: list[JobLink] = []
        for company in self.config.get("companies", []):
            try:
                self.endpoint = f"https://api.lever.co/v0/postings/{company}?mode=json"
                out.extend(self.parse(self.fetch_json(), company))
            except Exception:
                continue
        return out


class RssAdapter(SourceAdapter):
    feed_url: str = ""
    source_name: str = "RSS"
    source_domain: str = ""

    def _parse_rss(self, content: bytes) -> list[JobLink]:
        msg = BytesParser(policy=policy.default).parsebytes(content)
        text = msg.get_body(preferencelist=("plain", "html"))
        payload = text.get_content() if text else content.decode("utf-8", errors="ignore")
        # basic fallback parse for item/link
        links: list[JobLink] = []
        for part in payload.split("<item>")[1:]:
            if "<link>" in part:
                url = part.split("<link>", 1)[1].split("</link>", 1)[0].strip()
                links.append(JobLink(url, self.source_name, self.source_domain, {}))
        return links

    def search(self, profile: SearchProfile) -> list[JobLink]:
        _ = profile
        if not self.enabled:
            return []
        try:
            import httpx
            with httpx.Client(timeout=15) as client:
                r = client.get(self.feed_url)
                r.raise_for_status()
            txt = r.text
            links: list[JobLink] = []
            for part in txt.split("<item>")[1:]:
                if "<link>" in part:
                    url = part.split("<link>", 1)[1].split("</link>", 1)[0].strip()
                    links.append(JobLink(url, self.source_name, self.source_domain, {}))
            return links
        except Exception:
            return []


class WeWorkRemotelyRssAdapter(RssAdapter):
    name, domain = "weworkremotely_rss", "weworkremotely.com"
    feed_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    source_name = "We Work Remotely RSS"
    source_domain = "weworkremotely.com"


class RemoteOkRssAdapter(RssAdapter):
    name, domain = "remoteok_rss", "remoteok.com"
    feed_url = "https://remoteok.com/remote-dev-jobs.rss"
    source_name = "RemoteOK RSS"
    source_domain = "remoteok.com"


class CraigslistRssAdapter(RssAdapter):
    name, domain = "craigslist_rss", "craigslist.org"
    source_name = "Craigslist RSS"
    source_domain = "craigslist.org"

    def search(self, profile: SearchProfile) -> list[JobLink]:
        if not self.enabled:
            return []
        city = self.config.get("city", "sfbay")
        category = self.config.get("category", "sof")
        self.feed_url = f"https://{city}.craigslist.org/search/{category}?format=rss"
        return super().search(profile)


class GenericStubAdapter(StubAdapter):
    def __init__(self, config: dict[str, Any], name: str, domain: str) -> None:
        super().__init__(config)
        self.name = name
        self.domain = domain


def build_adapters(sources_cfg: dict[str, dict[str, Any]]) -> list[SourceAdapter]:
    fixed: dict[str, type[SourceAdapter]] = {
        "remoteok_api": RemoteOkAdapter,
        "remotive_api": RemotiveAdapter,
        "arbeitnow_api": ArbeitnowAdapter,
        "greenhouse_api": GreenhouseApiAdapter,
        "lever_api": LeverApiAdapter,
        "weworkremotely_rss": WeWorkRemotelyRssAdapter,
        "remoteok_rss": RemoteOkRssAdapter,
        "craigslist_rss": CraigslistRssAdapter,
    }
    adapters: list[SourceAdapter] = []
    for key, cfg in sources_cfg.items():
        cls = fixed.get(key)
        if cls:
            adapters.append(cls(cfg))
        else:
            adapters.append(GenericStubAdapter(cfg, key, cfg.get("domain", key)))
    return adapters


def apply_time_window(links: list[JobLink], profile: SearchProfile) -> list[JobLink]:
    cutoff = datetime.utcnow() - timedelta(hours=profile.time_window_hours)
    out: list[JobLink] = []
    for link in links:
        posted = link.snippet_meta.get("date") or link.snippet_meta.get("publication_date")
        if not posted:
            out.append(link)
            continue
        try:
            dt = datetime.fromisoformat(str(posted).replace("Z", "+00:00")).replace(tzinfo=None)
            if dt >= cutoff:
                out.append(link)
        except Exception:
            out.append(link)
    return out
