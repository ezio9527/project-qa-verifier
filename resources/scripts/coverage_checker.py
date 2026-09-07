#!/usr/bin/env python3
"""
Coverage Gate Checker for project-qa-verifier ecosystem.
Parses coverage reports (coverage-summary.json, pytest coverage.json, or lcov.info)
and enforces zero-compromise thresholds for lines, branches, functions, and statements.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_istanbul_summary(data: dict) -> dict:
    total = data.get("total", {})
    return {
        "lines": total.get("lines", {}).get("pct", 0.0),
        "branches": total.get("branches", {}).get("pct", 0.0),
        "functions": total.get("functions", {}).get("pct", 0.0),
        "statements": total.get("statements", {}).get("pct", 0.0),
    }


def parse_pytest_coverage(data: dict) -> dict:
    totals = data.get("totals", {})
    pct = totals.get("percent_covered", 0.0)
    return {
        "lines": round(pct, 2),
        "branches": round(pct, 2),
        "functions": round(pct, 2),
        "statements": round(pct, 2),
    }


def parse_lcov(lcov_path: Path) -> dict:
    lines_found = 0
    lines_hit = 0
    branches_found = 0
    branches_hit = 0
    functions_found = 0
    functions_hit = 0

    with open(lcov_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("LF:"):
                lines_found += int(line[3:])
            elif line.startswith("LH:"):
                lines_hit += int(line[3:])
            elif line.startswith("BRF:"):
                branches_found += int(line[4:])
            elif line.startswith("BRH:"):
                branches_hit += int(line[4:])
            elif line.startswith("FNF:"):
                functions_found += int(line[4:])
            elif line.startswith("FNH:"):
                functions_hit += int(line[4:])

    line_pct = (lines_hit / lines_found * 100.0) if lines_found > 0 else 0.0
    branch_pct = (branches_hit / branches_found * 100.0) if branches_found > 0 else 0.0
    fn_pct = (functions_hit / functions_found * 100.0) if functions_found > 0 else 0.0

    return {
        "lines": round(line_pct, 2),
        "branches": round(branch_pct, 2),
        "functions": round(fn_pct, 2),
        "statements": round(line_pct, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Enforce Coverage Gates")
    parser.add_argument("--report", required=True, help="Path to coverage report (JSON or LCOV)")
    parser.add_argument("--min-lines", type=float, default=80.0, help="Minimum line coverage percentage (default: 80.0)")
    parser.add_argument("--min-branches", type=float, default=75.0, help="Minimum branch coverage percentage (default: 75.0)")
    parser.add_argument("--min-functions", type=float, default=80.0, help="Minimum function coverage percentage (default: 80.0)")
    parser.add_argument("--min-statements", type=float, default=80.0, help="Minimum statement coverage percentage (default: 80.0)")
    args = parser.parse_args()

    report_path = Path(args.report).resolve()
    if not report_path.exists():
        print(f"[ERROR] Coverage report file not found: {report_path}")
        sys.exit(1)

    # Determine parser
    if report_path.suffix.lower() == ".json":
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "total" in data and isinstance(data["total"], dict):
            actual = parse_istanbul_summary(data)
        elif "totals" in data:
            actual = parse_pytest_coverage(data)
        else:
            print("[ERROR] Unrecognized JSON coverage format.")
            sys.exit(1)
    elif report_path.suffix.lower() in [".info", ".lcov"]:
        actual = parse_lcov(report_path)
    else:
        # Fallback probe
        with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            if first_line.startswith("TN:"):
                actual = parse_lcov(report_path)
            else:
                try:
                    f.seek(0)
                    data = json.load(f)
                    actual = parse_istanbul_summary(data)
                except Exception:
                    print(f"[ERROR] Unsupported coverage report format: {report_path}")
                    sys.exit(1)

    thresholds = {
        "lines": args.min_lines,
        "branches": args.min_branches,
        "functions": args.min_functions,
        "statements": args.min_statements,
    }

    print("=== [QA Coverage Gate Audit] ===")
    print(f"Report File: {report_path}")
    print(f"{'Metric':<14} | {'Target':<8} | {'Actual':<8} | {'Status'}")
    print("-" * 45)

    failed = False
    for metric, target in thresholds.items():
        val = actual.get(metric, 0.0)
        passed = val >= target
        status_str = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            failed = True
        print(f"{metric.capitalize():<14} | {target:>6.1f}% | {val:>6.1f}% | {status_str}")

    print("-" * 45)
    if failed:
        print("\n🚫 [GATE REJECTED] One or more coverage metrics failed to meet the required threshold.")
        print("   Ironclad Rule 3 Violation: Quality Gate failure is non-negotiable.")
        sys.exit(1)
    else:
        print("\n🎉 [GATE PASSED] All coverage metrics meet or exceed the required threshold.")
        sys.exit(0)


if __name__ == "__main__":
    main()
