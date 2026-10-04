#!/usr/bin/env python3
"""Add the exact run environment to one measured report."""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def main(project):
    reports = []
    for path in sorted(Path("results").glob("*/report.json")):
        report = json.loads(path.read_text())
        if project in report.get("projects", {}) and "environment" not in report:
            reports.append(report)
    if len(reports) != 1:
        raise RuntimeError(f"Expected one unstamped {project} report, found {len(reports)}")
    report = reports[0]
    versions = json.loads(Path(".benchmark-versions.json").read_text())
    target_sha = subprocess.check_output(
        ["git", "-C", f"workspace/{project}", "rev-parse", "HEAD"], text=True
    ).strip()
    report["environment"] = {
        "runner": os.getenv("RUNNER_NAME"),
        "image": os.getenv("ImageOS"),
        "image_version": os.getenv("ImageVersion"),
        "machine": platform.machine(),
        "kernel": platform.release(),
        "php": subprocess.check_output(["php", "-r", "echo PHP_VERSION;"], text=True),
        "project_commit": target_sha,
        "suite_commit": os.getenv("GITHUB_SHA"),
        "workflow_run": os.getenv("GITHUB_RUN_ID"),
        "timing_runs": 3,
        "memory_runs": 1,
        "versions": versions,
    }
    Path("artifact").mkdir(exist_ok=True)
    Path("artifact/report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
