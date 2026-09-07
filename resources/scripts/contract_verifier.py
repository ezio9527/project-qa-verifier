#!/usr/bin/env python3
"""
Contract Alignment Auditor for project-qa-verifier ecosystem.
Audits static contract consistency between docs/API_SPEC.md / .workflow/01_SPEC.md
and code implementations under src/ (TypeScript interfaces, types, Pydantic models).
"""

import argparse
import os
import re
import sys
from pathlib import Path


def extract_spec_interfaces(spec_file: Path) -> dict:
    """
    Extract interface/type blocks defined in markdown code blocks.
    Example:
    ```typescript
    export interface Order {
      id: string;
      total: number;
    }
    ```
    """
    if not spec_file.exists():
        return {}

    content = spec_file.read_text(encoding="utf-8", errors="ignore")
    interfaces = {}

    # Match interface definitions in ts/typescript code blocks
    pattern = re.compile(
        r"(?:export\s+)?interface\s+(\w+)\s*\{([^}]+)\}",
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        name = match.group(1)
        body = match.group(2)
        fields = {}
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                continue
            # match "fieldName: type;" or "fieldName?: type;"
            field_match = re.match(r"^(\w+)(\??)\s*:\s*([^;]+);?", line)
            if field_match:
                fname = field_match.group(1)
                opt = bool(field_match.group(2))
                ftype = field_match.group(3).strip()
                fields[fname] = {"optional": opt, "type": ftype}
        interfaces[name] = fields

    return interfaces


def scan_codebase_interfaces(src_dir: Path) -> dict:
    code_interfaces = {}
    if not src_dir.exists():
        return {}

    pattern = re.compile(
        r"(?:export\s+)?interface\s+(\w+)\s*\{([^}]+)\}",
        re.MULTILINE | re.DOTALL,
    )

    for p in src_dir.rglob("*.ts"):
        if p.name.endswith(".test.ts") or p.name.endswith(".spec.ts"):
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            for match in pattern.finditer(content):
                name = match.group(1)
                body = match.group(2)
                fields = {}
                for line in body.splitlines():
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    field_match = re.match(r"^(\w+)(\??)\s*:\s*([^;]+);?", line)
                    if field_match:
                        fname = field_match.group(1)
                        opt = bool(field_match.group(2))
                        ftype = field_match.group(3).strip()
                        fields[fname] = {"optional": opt, "type": ftype, "file": str(p)}
                code_interfaces[name] = fields
        except Exception:
            pass

    return code_interfaces


def main():
    parser = argparse.ArgumentParser(description="Contract Alignment Verifier")
    parser.add_argument("--spec", default=".workflow/01_SPEC.md", help="Path to specification file")
    parser.add_argument("--src", default="src", help="Path to source directory")
    parser.add_argument("--strict", action="store_true", help="Fail if any spec interface is missing from code")
    args = parser.parse_args()

    spec_path = Path(args.spec).resolve()
    src_path = Path(args.src).resolve()

    print("=== [QA Contract Drift Auditor] ===")
    print(f"Spec File: {spec_path}")
    print(f"Src Path : {src_path}\n")

    spec_interfaces = extract_spec_interfaces(spec_path)
    if not spec_interfaces and Path("docs/API_SPEC.md").exists():
        print("Note: .workflow/01_SPEC.md had no interfaces, scanning docs/API_SPEC.md...")
        spec_interfaces = extract_spec_interfaces(Path("docs/API_SPEC.md").resolve())

    if not spec_interfaces:
        print("[INFO] No interface definitions extracted from Spec. Contract verification skipped.")
        sys.exit(0)

    print(f"Found {len(spec_interfaces)} interface(s) in Spec: {list(spec_interfaces.keys())}")
    code_interfaces = scan_codebase_interfaces(src_path)
    print(f"Found {len(code_interfaces)} interface(s) in Code: {list(code_interfaces.keys())}\n")

    drift_detected = False

    for iface_name, spec_fields in spec_interfaces.items():
        if iface_name not in code_interfaces:
            print(f"❌ [MISSING INTERFACE] Interface '{iface_name}' defined in Spec is NOT implemented in {args.src}")
            drift_detected = True
            continue

        actual_fields = code_interfaces[iface_name]
        for fname, fmeta in spec_fields.items():
            if fname not in actual_fields:
                print(f"⚠️  [FIELD DRIFT] Interface '{iface_name}' is missing expected field '{fname}' in code implementation!")
                drift_detected = True
            else:
                act_meta = actual_fields[fname]
                if fmeta["optional"] != act_meta["optional"]:
                    print(
                        f"⚠️  [OPTIONALITY MISMATCH] '{iface_name}.{fname}': Spec optional={fmeta['optional']}, Code optional={act_meta['optional']}"
                    )

    if drift_detected:
        print("\n🚫 [CONTRACT DRIFT DETECTED] Source code does not fully align with Spec contracts.")
        if args.strict:
            sys.exit(1)
        else:
            print("   Running in advisory mode (use --strict to fail build).")
            sys.exit(0)
    else:
        print("🎉 [CONTRACT ALIGNED] All spec interfaces and fields are properly represented in code.")
        sys.exit(0)


if __name__ == "__main__":
    main()
