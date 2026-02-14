from __future__ import annotations

from jobpipeline.core.models import JobRecord


def dedupe_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    by_url: dict[str, JobRecord] = {}
    for job in jobs:
        existing = by_url.get(job.canonical_url)
        if not existing:
            by_url[job.canonical_url] = job
            continue
        existing.last_seen = job.last_seen
        existing.source_name = ",".join(sorted(set((existing.source_name + "," + job.source_name).split(","))))
        existing.merged_from.append(job.job_id)
    return list(by_url.values())
