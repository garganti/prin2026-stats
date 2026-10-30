#!/usr/bin/env python3
"""Run Python scripts from the project's code/ directory.

By default, only report-generating scripts are run. The data importers
(importa_*.py) and the shared helper module (prin_data.py) are skipped,
so the default run generates Markdown reports without rewriting Excel data.
Use --all to execute literally every .py file in code/.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CODE_DIR = PROJECT_ROOT / "code"
HELPER_MODULES = {"prin_data.py", "__init__.py"}


def discover_scripts(directory: Path, all_scripts: bool) -> list[Path]:
    scripts = sorted(directory.glob("*.py"), key=lambda p: p.name.casefold())
    scripts = [p for p in scripts if p.resolve() != Path(__file__).resolve()]
    if not all_scripts:
        scripts = [p for p in scripts if p.name not in HELPER_MODULES
                   and not p.name.startswith("importa_")]
    return scripts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Python programs in the code/ directory sequentially."
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run every .py file, including PDF-to-Excel importers and helper modules."
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List the selected scripts without running them."
    )
    parser.add_argument(
        "--stop-on-error", action="store_true",
        help="Stop immediately if a script exits with an error."
    )
    parser.add_argument(
        "--code-dir", type=Path, default=CODE_DIR,
        help="Override the code/ directory (useful for tests)."
    )
    args = parser.parse_args()

    code_dir = args.code_dir.resolve()
    if not code_dir.is_dir():
        parser.error(f"Code directory not found: {code_dir}")
    scripts = discover_scripts(code_dir, args.all)
    if not scripts:
        print(f"No Python scripts found in {code_dir}", file=sys.stderr)
        return 1

    if args.list:
        for script in scripts:
            print(script.name)
        return 0

    successes = []
    failures = []
    total = len(scripts)
    start = time.monotonic()
    for index, script in enumerate(scripts, 1):
        print(f"\n[{index}/{total}] Running {script.name}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=PROJECT_ROOT,
                check=False,
            )
            exit_code = result.returncode
        except OSError as error:
            print(f"Cannot start {script.name}: {error}", file=sys.stderr)
            exit_code = 1
        if exit_code == 0:
            successes.append(script.name)
            print(f"OK: {script.name}", flush=True)
        else:
            failures.append((script.name, exit_code))
            print(f"FAILED: {script.name} (exit code: {exit_code})", file=sys.stderr, flush=True)
            if args.stop_on_error:
                break

    print(f"\nCompleted in {time.monotonic() - start:.1f} seconds: "
          f"{len(successes)} successful, {len(failures)} failed.")
    if failures:
        for name, code in failures:
            print(f"  - {name}: exit code {code}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
