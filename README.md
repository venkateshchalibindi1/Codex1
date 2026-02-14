# JobPipeline

Local-first native desktop job-search tool for Windows. It searches configured sources, collects details, deduplicates, scores fit, and syncs to Excel. It does **not** auto-apply.

## Install
```bash
python -m pip install -e ".[dev]" --no-build-isolation
```

## Run
```bash
# CLI pipeline run
jobpipeline-cli

# Desktop UI
jobpipeline-ui
```

## Tests
```bash
pytest -q
```

## Supported Sources
Enabled now by default: RemoteOK API, Remotive API, Arbeitnow API, Greenhouse API, Lever API, WeWorkRemotely RSS, RemoteOK RSS, Craigslist RSS.

Configured as stubs (enabled=false by default, fail-soft, TODO-backed): Ashby, Workable, USAJobs, Adzuna, Jooble, Authentic Jobs, Stack Overflow Jobs RSS, GitHub Jobs legacy, HiringCafe, Idealist, SimplyHired, Dice, CareerJet, Reed, The Muse, Jobspresso, Snagajob, GovernmentJobs, HigherEdJobs, Relocate.me, Behance, ProBlogger, Landing.jobs.

## Freshness-first behavior
`profiles[].time_window_hours` uses hours (default 24). Scoring includes freshness bonus and filters recent posts first when timestamps are available.

## Safety
- No CAPTCHA/login wall bypass.
- LinkedIn behind auth is out of scope.
- Respect throttling/retries.
- Web discovery is optional and disabled by default when provider keys are absent.

## Data outputs
Defaults to `C:/Users/Public/JobPipeline` (outside repo root):
- `jobpipeline.sqlite`
- `jobpipeline_tracker.xlsx`
- logs under `logs/`

## Excel sync guarantees
Sheet name: `Jobs`.
Updates non-user columns for existing Job ID rows, preserving `Status` and `Notes`.
