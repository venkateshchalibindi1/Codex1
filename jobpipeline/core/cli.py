from __future__ import annotations

from jobpipeline.core.models import SearchProfile
from jobpipeline.core.pipeline import PipelineService
from jobpipeline.utils.config import load_config


def main() -> None:
    cfg = load_config()
    p = cfg["profiles"][0]
    profile = SearchProfile(**p)
    service = PipelineService(cfg)
    jobs = service.run(profile)
    print(f"Collected {len(jobs)} jobs")


if __name__ == "__main__":
    main()
