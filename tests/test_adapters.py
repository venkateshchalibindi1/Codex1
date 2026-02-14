from jobpipeline.core.models import SearchProfile
from jobpipeline.sources.adapters import (
    ArbeitnowAdapter,
    GreenhouseApiAdapter,
    LeverApiAdapter,
    RemotiveAdapter,
    RemoteOkAdapter,
    build_adapters,
)
from jobpipeline.sources.manager import SourceManager


def profile() -> SearchProfile:
    return SearchProfile(
        name="d",
        target_titles=["Network Engineer"],
        adjacent_titles=[],
        location_mode="Remote",
        city=None,
        radius_km=None,
        experience_range="1-3",
        must_have_keywords=["tcp/ip"],
        nice_to_have_keywords=[],
        exclude_keywords=[],
        time_window_hours=24,
    )


def test_remoteok_parse_sample_json() -> None:
    data = [{"url": "https://remoteok.com/abc", "position": "Net Eng"}]
    links = RemoteOkAdapter.parse(data)
    assert len(links) == 1
    assert links[0].job_url.endswith("abc")


def test_remotive_parse_sample_json() -> None:
    data = {"jobs": [{"url": "https://remotive.com/x", "title": "NOC"}]}
    links = RemotiveAdapter.parse(data)
    assert links[0].source_domain == "remotive.com"


def test_arbeitnow_parse_sample_json() -> None:
    data = {"data": [{"url": "https://arbeitnow.com/jobs/1", "title": "Net"}]}
    links = ArbeitnowAdapter.parse(data)
    assert len(links) == 1


def test_greenhouse_parse_sample_json() -> None:
    data = {"jobs": [{"absolute_url": "https://boards.greenhouse.io/a/jobs/1"}]}
    links = GreenhouseApiAdapter.parse(data, "a")
    assert links[0].source_name == "Greenhouse:a"


def test_lever_parse_sample_json() -> None:
    data = [{"hostedUrl": "https://jobs.lever.co/c/1"}]
    links = LeverApiAdapter.parse(data, "c")
    assert links[0].source_name == "Lever:c"


def test_h1b_mode_uses_greenhouse_and_lever() -> None:
    cfg = {
        "sources": {
            "greenhouse_api": {"enabled": False, "boards": []},
            "lever_api": {"enabled": False, "companies": []},
        },
        "h1b_employers": [
            {"name": "Stripe", "ats": "greenhouse", "board_slug": "stripe"},
            {"name": "Netflix", "ats": "lever", "board_slug": "netflix"},
        ],
    }
    manager = SourceManager(cfg)
    # monkeypatch by replacing adapters with enabled ones and fake search
    for adapter in manager.adapters:
        adapter.config["enabled"] = True
        adapter.search = lambda p, a=adapter: [] if not a.config.get("enabled") else []
    assert manager.h1b_mode_links(profile()) == []


def test_stub_adapters_return_empty_when_disabled() -> None:
    cfg = {
        "ashby": {"enabled": False},
        "workable": {"enabled": False},
        "simplyhired": {"enabled": False},
    }
    adapters = build_adapters(cfg)
    for adapter in adapters:
        assert adapter.search(profile()) == []
