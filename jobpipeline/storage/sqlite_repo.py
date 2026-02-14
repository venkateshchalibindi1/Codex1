from __future__ import annotations

import sqlite3
from pathlib import Path

from jobpipeline.core.models import JobRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    source_domain TEXT, source_name TEXT, job_url TEXT, canonical_url TEXT,
    apply_url TEXT, title TEXT, company TEXT, location_text TEXT, remote_flag TEXT,
    employment_type TEXT, posted_date TEXT, collected_at TEXT, description_raw TEXT,
    salary_text TEXT, skills_extracted TEXT, fetch_status TEXT, failure_reason TEXT,
    first_seen TEXT, last_seen TEXT, repost_count INTEGER, merged_from TEXT,
    fit_score INTEGER, fit_grade TEXT, fit_notes TEXT, missing_must_have TEXT,
    flags TEXT, user_status TEXT, user_notes TEXT
);
CREATE TABLE IF NOT EXISTS job_sources_seen (job_id TEXT, source_name TEXT, source_domain TEXT);
CREATE TABLE IF NOT EXISTS runs (run_id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT, finished_at TEXT, num_found INTEGER, num_collected INTEGER, num_failed INTEGER, num_merged INTEGER, num_exported INTEGER);
CREATE TABLE IF NOT EXISTS run_errors (run_id INTEGER, domain TEXT, reason TEXT, trace_summary TEXT);
"""


class SQLiteRepo:
    def __init__(self, db_path: str) -> None:
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def upsert_job(self, job: JobRecord) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                job.job_id, job.source_domain, job.source_name, job.job_url, job.canonical_url,
                job.apply_url, job.title, job.company, job.location_text, job.remote_flag, job.employment_type,
                job.posted_date, job.collected_at, job.description_raw, job.salary_text, ",".join(job.skills_extracted),
                job.fetch_status, job.failure_reason, job.first_seen, job.last_seen, job.repost_count, ",".join(job.merged_from),
                job.fit_score, job.fit_grade, job.fit_notes, ",".join(job.missing_must_have), ",".join(job.flags),
                job.user_status, job.user_notes,
            ),
        )
        self.conn.commit()
