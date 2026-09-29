#!/usr/bin/env python3
"""Freeze current package releases and PHPStan's 2.3.x commit for one run."""

import json
import os
import re
import urllib.request
from pathlib import Path


PACKAGES = [
    ("mago", "carthage-software/mago"),
    ("pretty-php", "lkrms/pretty-php"),
    ("php-cs-fixer", "php-cs-fixer/shim"),
    ("phpcs", "squizlabs/php_codesniffer"),
    ("phpstan", "phpstan/phpstan"),
    ("psalm", "vimeo/psalm"),
    ("phan", "phan/phan"),
]


def get_json(url):
    headers = {"User-Agent": "php-toolchain-benchmarks"}
    token = os.getenv("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def latest_stable(package):
    data = get_json(f"https://repo.packagist.org/p2/{package}.json")
    versions = (entry["version"] for entry in data["packages"][package])
    stable = [v for v in versions if re.fullmatch(r"v?\d+\.\d+\.\d+", v)]
    if not stable:
        raise RuntimeError(f"No stable three-part version for {package}")
    return max(stable, key=lambda v: tuple(map(int, v.lstrip("v").split("."))))


def main():
    resolved = []
    for name, package in PACKAGES:
        version = latest_stable(package)
        resolved.append([name, package, version])
        print(f"{name}: {version}")

        if name == "phpstan":
            branch = get_json("https://api.github.com/repos/phpstan/phpstan/branches/2.3.x")
            sha = branch["commit"]["sha"]
            version = f"2.3.x-dev#{sha}"
            resolved.append(["phpstan-next", package, version])
            print(f"phpstan-next: {version}")

    Path(".benchmark-versions.json").write_text(json.dumps(resolved, indent=2) + "\n")


if __name__ == "__main__":
    main()
