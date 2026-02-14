from __future__ import annotations

from datetime import datetime, timedelta
import re

from jobpipeline.core.models import JobRecord, SearchProfile
from jobpipeline.utils.text import normalize_skill


FLAG_PATTERNS = {
    "clearance": ["clearance", "ts/sci", "top secret"],
    "us_citizen_only": ["us citizen", "u.s. citizen"],
    "no_sponsorship": ["no sponsorship", "visa not supported"],
    "onsite_required": ["onsite", "on-site"],
    "contract": ["contract", "c2c"],
}


def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    return "D"


def score_job(job: JobRecord, profile: SearchProfile) -> JobRecord:
    text = f"{job.title} {job.description_raw}".lower()
    must = [normalize_skill(x) for x in profile.must_have_keywords]
    nice = [normalize_skill(x) for x in profile.nice_to_have_keywords]

    missing = [m for m in must if m and m not in text]
    must_score = int((len(must) - len(missing)) / max(len(must), 1) * 40)
    nice_score = min(20, sum(1 for n in nice if n and n in text) * 4)
    title_score = 20 if any(t.lower() in job.title.lower() for t in profile.target_titles + profile.adjacent_titles) else 5
    location_score = 10 if profile.location_mode.lower() == "remote" and "remote" in job.location_text.lower() else 5

    freshness = 0
    if job.posted_date:
        try:
            posted = datetime.fromisoformat(job.posted_date.replace("Z", "+00:00")).replace(tzinfo=None)
            freshness = 10 if posted >= datetime.utcnow() - timedelta(hours=profile.time_window_hours) else 2
        except Exception:
            freshness = 3

    score = min(100, must_score + nice_score + title_score + location_score + freshness)
    flags: list[str] = []
    for flag, patterns in FLAG_PATTERNS.items():
        if any(p in text for p in patterns):
            flags.append(flag)
            if flag in {"clearance", "us_citizen_only", "no_sponsorship"}:
                score = min(score, 40)

    years = re.findall(r"(\d+)\+?\s+years", text)
    if years and int(years[0]) > int(profile.experience_range.split("-")[-1]):
        score -= 10

    job.fit_score = max(0, score)
    job.fit_grade = _grade(job.fit_score)
    job.missing_must_have = missing
    job.flags = sorted(set(flags))
    job.fit_notes = f"must_match={len(must)-len(missing)}/{len(must)}; flags={','.join(job.flags) or 'none'}; freshness={freshness}"
    return job
