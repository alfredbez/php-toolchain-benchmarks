#!/usr/bin/env python3
"""Copy one report per target project into the public history."""

import json
import os
import shutil
from pathlib import Path


def main():
    run_id = os.environ["GITHUB_RUN_ID"]
    for project in ("psl", "wordpress", "magento"):
        source = Path(f"incoming/benchmark-{project}/report.json")
        report = json.loads(source.read_text())
        if project not in report["projects"]:
            raise RuntimeError(f"Report {source} has no {project} results")
        destination = Path(f"results/{run_id}-{project}/report.json")
        destination.parent.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(source, destination)
        print(destination)


if __name__ == "__main__":
    main()
