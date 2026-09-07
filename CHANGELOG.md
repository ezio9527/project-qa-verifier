# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-07

### Added
- **Core Engine**: Initial release of `project-qa-verifier` - Autonomous Multi-Agent Quality Assurance and Gatekeeper Engine.
- **The Five Ironclad QA Rules**:
  - Rule 1: Zero Business Code Mutation (pure test assets, zero changes to `src/*`).
  - Rule 2: Adversarial & Boundary Verification (fuzzing, race condition, fault injection, security).
  - Rule 3: Hard Quality Gates & Zero Compromise (coverage, lint/type check, regression zero-tolerance).
  - Rule 4: Dual-Track Defect Triaging & Repro Invariant (Red test case repro, implementation bug vs. architecture RFC).
  - Rule 5: State Bus Atomicity & Traceability (`.workflow/state.json` and `03_TEST_REPORT.md` synchronization).
- **Penta-Mode Engine**:
  - Mode A: Full Acceptance & Contract Audit (`/qa-accept`, `/verify`).
  - Mode B: Adversarial & Chaos Testing (`/qa-chaos`, `/qa-fuzz`).
  - Mode C: Performance Benchmark & Regression Audit (`/qa-perf`, `/qa-regression`).
  - Mode D: Defect Repro & Root-Cause Triage (`/qa-triage`, `/qa-repro`).
  - Mode E: Brownfield QA Healthcheck (`/qa-health`, `/qa-audit`).
- **Tooling Suite**:
  - `resources/scripts/qa_runner.py`: Unified test execution runner and report builder.
  - `resources/scripts/coverage_checker.py`: Strong coverage gate checker for lcov/json reports.
  - `resources/scripts/contract_verifier.py`: Contract drift auditor for models and endpoints.
- **Templates**:
  - `.workflow/03_TEST_REPORT.md`: Comprehensive test report deliverable.
  - `.workflow/feedback/RFC_TO_ARCHITECT.md`: Blocker escalation template for architectural/contract issues.
  - Sample test configuration templates for Vitest, Pytest, and k6.
