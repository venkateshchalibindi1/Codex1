from __future__ import annotations

from jobpipeline.collectors.parser import parse_job_html
from jobpipeline.core.models import JobRecord, SearchProfile
from jobpipeline.dedupe.engine import dedupe_jobs
from jobpipeline.export.excel_sync import sync_excel
from jobpipeline.scoring.engine import score_job
from jobpipeline.sources.manager import SourceManager
from jobpipeline.storage.sqlite_repo import SQLiteRepo


class DisabledDiscoveryProvider:
    def discover(self, query: str) -> list[str]:
        _ = query
        return []


class PipelineService:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.sources = SourceManager(cfg)
        self.repo = SQLiteRepo(cfg["storage"]["sqlite_path"])
        self.discovery_provider = DisabledDiscoveryProvider()

    def run(self, profile: SearchProfile) -> list[JobRecord]:
        links = self.sources.search(profile)
        jobs: list[JobRecord] = []
        for link in links:
            parsed = parse_job_html(f"<html><body><h1>{link.snippet_meta.get('position','Job')}</h1></body></html>")
            jobs.append(JobRecord.from_link(link, **parsed))
        jobs = dedupe_jobs(jobs)
        jobs = [score_job(j, profile) for j in jobs]
        for job in jobs:
            self.repo.upsert_job(job)
        sync_excel(self.cfg["excel_path"], jobs)
        return jobs
