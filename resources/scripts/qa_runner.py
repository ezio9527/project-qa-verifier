#!/usr/bin/env python3
"""
Unified QA Test Runner for project-qa-verifier ecosystem.
Executes test commands, captures timings, extracts pass/fail metrics,
and enforces zero-compromise test exit codes.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def parse_test_metrics(output: str) -> dict:
    """
    Attempt to extract test statistics from common runners (vitest, jest, pytest).
    """
    metrics = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "total": 0,
        "framework": "unknown",
    }

    # Vitest / Jest matcher
    # e.g.: "Tests  2 passed (2)" or "Tests: 2 passed, 1 failed, 3 total"
    vitest_match = re.search(r"Tests\s+.*?((\d+)\s+passed)?.*?((\d+)\s+failed)?.*?((\d+)\s+skipped)?.*?\(?(\d+)\)?", output, re.IGNORECASE)
    if "vitest" in output.lower() or "jest" in output.lower():
        metrics["framework"] = "vitest/jest"
        p = re.search(r"(\d+)\s+passed", output)
        f = re.search(r"(\d+)\s+failed", output)
        s = re.search(r"(\d+)\s+skipped", output)
        if p:
            metrics["passed"] = int(p.group(1))
        if f:
            metrics["failed"] = int(f.group(1))
        if s:
            metrics["skipped"] = int(s.group(1))
        metrics["total"] = metrics["passed"] + metrics["failed"] + metrics["skipped"]
        return metrics

    # Pytest matcher
    # e.g.: "= 5 passed, 1 failed, 2 skipped in 0.12s ="
    pytest_match = re.search(r"=+\s*(.*?)\s+in\s+[\d\.]+s\s*=+", output)
    if pytest_match or "pytest" in output.lower():
        metrics["framework"] = "pytest"
        p = re.search(r"(\d+)\s+passed", output)
        f = re.search(r"(\d+)\s+failed", output)
        s = re.search(r"(\d+)\s+skipped", output)
        if p:
            metrics["passed"] = int(p.group(1))
        if f:
            metrics["failed"] = int(f.group(1))
        if s:
            metrics["skipped"] = int(s.group(1))
        metrics["total"] = metrics["passed"] + metrics["failed"] + metrics["skipped"]
        return metrics

    return metrics


def main():
    parser = argparse.ArgumentParser(description="QA Test Execution Runner")
    parser.add_argument("--command", required=True, help="Test command to execute (e.g. 'npm test')")
    parser.add_argument("--type", default="unit", choices=["lint", "unit", "integration", "e2e", "chaos", "regression", "perf"], help="Test type label")
    parser.add_argument("--timeout", type=int, default=300, help="Execution timeout in seconds")
    parser.add_argument("--output-json", help="Optional path to output execution summary JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    print(f"=== [QA Runner] Type: {args.type.upper()} ===")
    print(f"Command: {args.command}")
    print(f"Timeout: {args.timeout}s\n")

    if args.dry_run:
        print("[DRY-RUN] Command skipped.")
        sys.exit(0)

    start_time = time.time()
    try:
        res = subprocess.run(
            args.command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=args.timeout,
        )
        duration = time.time() - start_time
        stdout = res.stdout or ""
        stderr = res.stderr or ""
        exit_code = res.returncode
    except subprocess.TimeoutExpired as te:
        duration = time.time() - start_time
        stdout = te.stdout or ""
        stderr = f"[TIMEOUT] Command exceeded {args.timeout} seconds.\n" + (te.stderr or "")
        exit_code = 124

    # Print streams
    if stdout:
        print("--- Standard Output ---")
        print(stdout)
    if stderr:
        print("--- Standard Error ---")
        print(stderr)

    # Parse metrics
    combined_output = stdout + "\n" + stderr
    metrics = parse_test_metrics(combined_output)

    summary = {
        "type": args.type,
        "command": args.command,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 2),
        "status": "PASSED" if exit_code == 0 else "FAILED",
        "metrics": metrics,
    }

    print("\n=== [QA Runner Summary] ===")
    print(f"Verdict : {summary['status']}")
    print(f"ExitCode: {exit_code}")
    print(f"Duration: {summary['duration_seconds']}s")
    if metrics["total"] > 0:
        print(f"Stats   : {metrics['passed']} passed, {metrics['failed']} failed, {metrics['skipped']} skipped (Total: {metrics['total']})")

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Saved summary to: {out_path}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
