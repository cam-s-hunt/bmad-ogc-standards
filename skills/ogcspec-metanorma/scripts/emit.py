#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""emit: turn ModSpec requirement records (YAML) into Metanorma AsciiDoc fragments.

The YAML records are the source of truth; the AsciiDoc is generated and is not edited by hand. The
fragments are meant to be `include::`d by a document whose header, prose and bibliography the
project owns. Nothing here invents content: a field the record does not carry is not emitted.

Prose (statement, purpose, steps) is emitted as literal text, so AsciiDoc markup in a record is not
interpreted: `*x*`, `_x_`, `<<x>>`, `{x}` and URLs come back as written. Metanorma's own typography still
applies afterwards (`--` becomes a dash, straight quotes become curly); the gate's fidelity check
normalises exactly those. Formatted prose (emphasis, cross-references) is therefore not expressible in a
record yet.

Record kinds and fields are those of the gate (see ogcspec-gate/scripts/gate.py). One field is
emitter-only: abstract_test may carry `steps: [..]`, emitted as the test-method. No steps, no
test-method; the gate does not require one, a human or the 25-001 policy decides whether it must.

Usage:
  emit.py --records <dir> --out <dir>

Writes conformance-classes.adoc, requirements.adoc and abstract-tests.adoc. Same input, same bytes.
Exit 0 written; 2 usage error or an unreadable record.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ORDER = ("requirements_class", "requirement", "recommendation", "permission", "abstract_test", "conformance_class")


def load(directory: Path) -> list[dict]:
    out: list[dict] = []
    for path in sorted(directory.rglob("*.y*ml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for item in data if isinstance(data, list) else [data]:
            if not isinstance(item, dict):
                raise ValueError(f"{path.name}: record is not a mapping")
            out.append(item)
    return out


def one_line(value: object) -> str:
    return " ".join(str(value).split())


def literal(value: object) -> str:
    """Prose as literal text: AsciiDoc's inline macros, formatting and replacements are not applied
    (pass:c[...] keeps only XML escaping). A closing bracket is escaped with a backslash; a backslash
    directly before one cannot be told apart from that escape, so it is refused."""
    text = one_line(value)
    if "\\]" in text:
        raise ValueError(f"cannot emit a backslash directly before ']': {text[:60]!r}")
    return "pass:c[" + text.replace("]", "\\]") + "]"


def block(style: str, fields: list[tuple[str, str]], extra: str = "") -> str:
    lines = [style, "====", "[%metadata]"]
    lines += [f"{key}:: {one_line(value)}" for key, value in fields]
    if extra:
        lines.append(extra.rstrip("\n"))
    lines.append("====")
    return "\n".join(lines) + "\n"


def emit_record(r: dict) -> str:
    kind, ident = r["kind"], r["id"]
    if kind == "requirements_class":
        fields = [("identifier", ident)]
        if r.get("subject"):
            fields.append(("subject", r["subject"]))
        fields += [("inherit", d) for d in r.get("inherit") or []]
        fields += [("requirement", q) for q in r.get("requirements") or []]
        return block("[requirements_class]", fields)
    if kind in ("requirement", "recommendation", "permission"):
        return block(f"[{kind},model=ogc]", [("identifier", ident), ("part", literal(r.get("statement", "")))])
    if kind == "abstract_test":
        fields = [("identifier", ident), ("target", r.get("target", ""))]
        if r.get("purpose"):
            fields.append(("test-purpose", literal(r["purpose"])))
        extra = ""
        if r.get("steps"):
            steps = "\n".join(f"step::: {literal(s)}" for s in r["steps"])
            extra = f"test-method::\n+\n--\n{steps}\n--"
        return block("[abstract_test]", fields, extra)
    if kind == "conformance_class":
        fields = [("identifier", ident), ("target", r.get("target", ""))]
        fields += [("conformance-test", t) for t in r.get("tests") or []]
        return block("[conformance_class]", fields)
    raise ValueError(f"cannot emit kind {kind!r} ({ident!r})")


def emit(records: list[dict]) -> dict[str, str]:
    for r in records:  # refuse rather than silently drop a record the emitter does not know
        if r.get("kind") not in ORDER or not isinstance(r.get("id"), str):
            raise ValueError(f"cannot emit record with kind {r.get('kind')!r} and id {r.get('id')!r}")
    def part(kinds: tuple[str, ...]) -> str:
        chosen = sorted((r for r in records if r.get("kind") in kinds), key=lambda r: (ORDER.index(r["kind"]), r["id"]))
        return "\n".join(emit_record(r) for r in chosen)

    return {
        "conformance-classes.adoc": part(("conformance_class",)),
        "requirements.adoc": part(("requirements_class", "requirement", "recommendation", "permission")),
        "abstract-tests.adoc": part(("abstract_test",)),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Emit Metanorma AsciiDoc from requirement records.")
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.records.is_dir():
        print(f"records directory not found: {args.records}", file=sys.stderr)
        return 2
    try:
        files = emit(load(args.records))
    except (ValueError, KeyError, yaml.YAMLError) as error:
        print(f"cannot emit: {error}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
