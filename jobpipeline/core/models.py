from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import hashlib


@dataclass(slots=True)
class SearchProfile:
    name: str
    target_titles: list[str]
    adjacent_titles: list[str]
    location_mode: str
    city: str | None
    radius_km: int | None
    experience_range: str
    must_have_keywords: list[str]
    nice_to_have_keywords: list[str]
    exclude_keywords: list[str]
    time_window_hours: int = 24


@dataclass(slots=True)
class JobLink:
    job_url: str
    source_name: str
    source_domain: str
    snippet_meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JobRecord:
    job_id: str
    source_domain: str
    source_name: str
    job_url: str
    canonical_url: str
    apply_url: str | None
    title: str
    company: str
    location_text: str
    remote_flag: str
    employment_type: str
    posted_date: str | None
    collected_at: str
    description_raw: str
    salary_text: str | None
    skills_extracted: list[str]
    fetch_status: str
    failure_reason: str | None
    first_seen: str
    last_seen: str
    repost_count: int
    merged_from: list[str]
    fit_score: int
    fit_grade: str
    fit_notes: str
    missing_must_have: list[str]
    flags: list[str]
    user_status: str = "New"
    user_notes: str = ""
    possible_duplicate: bool = False

    @staticmethod
    def create_id(url: str, company: str, title: str) -> str:
        raw = f"{url}|{company}|{title}".encode("utf-8")
        return hashlib.sha1(raw).hexdigest()[:16]

    @classmethod
    def from_link(cls, link: JobLink, **kwargs: Any) -> "JobRecord":
        now = datetime.utcnow().isoformat()
        url = kwargs.get("canonical_url", link.job_url)
        company = kwargs.get("company", "Unknown")
        title = kwargs.get("title", "Unknown")
        return cls(
            job_id=cls.create_id(url, company, title),
            source_domain=link.source_domain,
            source_name=link.source_name,
            job_url=link.job_url,
            canonical_url=url,
            apply_url=kwargs.get("apply_url"),
            title=title,
            company=company,
            location_text=kwargs.get("location_text", "Unknown"),
            remote_flag=kwargs.get("remote_flag", "Unknown"),
            employment_type=kwargs.get("employment_type", "Unknown"),
            posted_date=kwargs.get("posted_date"),
            collected_at=now,
            description_raw=kwargs.get("description_raw", ""),
            salary_text=kwargs.get("salary_text"),
            skills_extracted=kwargs.get("skills_extracted", []),
            fetch_status=kwargs.get("fetch_status", "success"),
            failure_reason=kwargs.get("failure_reason"),
            first_seen=now,
            last_seen=now,
            repost_count=0,
            merged_from=[],
            fit_score=0,
            fit_grade="D",
            fit_notes="",
            missing_must_have=[],
            flags=[],
        )
