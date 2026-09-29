# PHP toolchain benchmarks

Weekly measurements of current PHP formatters, linters and static analyzers on three open-source projects. This repository is a fork of [carthage-software/php-toolchain-benchmarks](https://github.com/carthage-software/php-toolchain-benchmarks). The measurement engine and dashboard started there; this fork adds a scheduled GitHub Actions run and Linux support.

[Results](https://alfredbez.github.io/php-toolchain-benchmarks/)

## What is measured

| Category | Tools |
| --- | --- |
| Formatters | Mago Fmt, Pretty PHP |
| Linters | Mago Lint, PHP-CS-Fixer, PHPCS |
| Analyzers | Mago, PHPStan stable, PHPStan 2.3.x, PHPStan stable with bleedingEdge, Psalm, Phan |

The targets are `php-standard-library/php-standard-library`, `WordPress/wordpress-develop` and `magento/magento2`. Each project is measured on one `ubuntu-24.04` runner. Runs happen in separate jobs, so measurements from different projects are not directly comparable.

Before each weekly run, `scripts/resolve_versions.py` selects the latest stable release of every Composer package. It also pins PHPStan's `2.3.x` branch to an exact Git commit. The resolved versions, project commit, runner image, PHP version and suite commit are saved with each raw report. A new package release can change the measured behavior, including the errors reported by an analyzer.

For each scenario the profiler makes three timed runs and one separate memory run. Memory is the peak *sampled sum of RSS* over the process tree at 50 ms intervals; short runs are cross-checked with `/usr/bin/time`. The memory number can miss a brief spike and is not the same as unique physical memory. Analyzer results include cold runs with caches cleared and hot runs with caches warmed. Phan uses one worker and is omitted on Magento after two hosted runners shut down during that workload; the runner logs do not identify the cause. A tool whose cold run times out is omitted from the hot run. Each invocation has a ten-minute timeout.

**Interpretation:** Compare tools only within the same project and weekly run. GitHub-hosted hardware and background load vary. The dashboard shows one complete run per project in its overview and keeps older reports as history; it does not use week-over-week deltas as a performance claim. The tools apply different rules and can report different findings, so a faster result does not imply equivalent analysis. These measurements do not establish absolute speed or memory use on your machine.

The workflow runs every Sunday at 03:17 UTC and can also be started manually from the Actions tab. If setup, stability checks or a measurement fail, the workflow does not publish a partial new week.

## Run locally

Requires PHP 8.5, Composer and Python 3. Run from the repository root:

```sh
composer install
python3 scripts/resolve_versions.py
php src/main.php setup --project psl
php src/main.php run --project psl --runs 3 --timeout 3
php src/main.php build
```

Open `results/index.html`. Omit `--project psl` from setup and run to include all targets. The optional `--kind` and `--tool` filters are listed by `php src/main.php help`.

## License

MIT, as in the upstream project. See [LICENSE](LICENSE).
