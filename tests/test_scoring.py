from datetime import datetime

from jobpipeline.core.models import JobLink, JobRecord, SearchProfile
from jobpipeline.scoring.engine import score_job


def test_freshness_and_flags() -> None:
    p = SearchProfile("d", ["Network Engineer"], [], "Remote", None, None, "1-3", ["tcp/ip"], ["palo alto"], [], 24)
    link = JobLink("https://x", "s", "d", {})
    j = JobRecord.from_link(
        link,
        title="Network Engineer",
        company="ACME",
        location_text="Remote",
        description_raw="Requires tcp/ip and paloalto, no sponsorship and ts/sci clearance",
        posted_date=datetime.utcnow().isoformat(),
    )
    j = score_job(j, p)
    assert "clearance" in j.flags
    assert j.fit_grade in {"C", "D"}
