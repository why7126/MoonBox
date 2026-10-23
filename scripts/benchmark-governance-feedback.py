#!/usr/bin/env python3
"""Measure governance CLI overhead in a disposable local ledger, without claiming savings."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=20)
    args = parser.parse_args()
    if not 3 <= args.iterations <= 100:
        parser.error("iterations must be between 3 and 100")
    starts, finishes = [], []
    with tempfile.TemporaryDirectory(prefix="governance-benchmark-") as directory:
        cli = [sys.executable, str(ROOT / "scripts/governance_feedback.py"), "--store", directory]
        for _ in range(args.iterations):
            before = time.perf_counter()
            result = subprocess.run(cli + [
                "start", "--command", "benchmark", "--task-class", "cli-overhead",
                "--model", "none", "--environment", "local", "--validation-profile", "lifecycle",
                "--workload-key", "empty-run"], capture_output=True, text=True, check=True)
            starts.append(time.perf_counter() - before)
            run_id = json.loads(result.stdout)["id"]
            before = time.perf_counter()
            subprocess.run(cli + ["finish", run_id, "--status", "passed", "--quality", "passed"],
                           capture_output=True, check=True)
            finishes.append(time.perf_counter() - before)
    def summary(values):
        return {"median_ms": round(statistics.median(values) * 1000, 3),
                "p95_ms": round(sorted(values)[max(0, (95 * len(values) + 99) // 100 - 1)] * 1000, 3)}
    print(json.dumps({"measurement": "local-cli-overhead", "samples": args.iterations,
                      "start": summary(starts), "finish_and_review": summary(finishes),
                      "total_seconds": round(sum(starts + finishes), 3),
                      "tokens": None, "benefit_status": "not-evaluated"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
