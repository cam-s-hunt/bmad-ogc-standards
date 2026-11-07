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

Added by record-format-proposal.md (plan step 3):
  title        on a requirements_class or conformance_class: written as the block title, as literal text
               (`.pass:c[...]`); a plain block title applies inline markup and can produce XML errors (observed).
  inherit::    on every conformance_class: the conformance classes it depends on (Req 12). Dependencies inside the
               document are derived from the requirements class's `inherit` through the one-to-one Req 8
               correspondence; the authored `depends_on` entries (outside the document) follow. `conformance_inherit`
               below is an identical copy of the gate's function of the same name; a test keeps them equal and the
               gate's stage 2 (X003) compares the result with the compiled document.
  Record-only fields (`status`, `uml_package`, `profile`, `depends_on` as such) are not emitted as themselves.
  A profile is two ordinary blocks: a requirements_class with no requirements and a conformance_class with no tests.

Terms (term-record-proposal.md): a `term` record becomes one terminological entry in terms.adoc, written to be
`include::`d inside the project's own terms clause, which must be marked `[heading=terms and definitions]` (observed: without
it Metanorma aborts, STANDOC_25) and which Metanorma's OGC flavour precedes with its own boilerplate. The entry is
`=== pass:c[term]`, one `alt:[pass:c[alias]]` line per alias, the definition as literal text, the term's own `note` as `NOTE:`, and
`[.source]` with the citation (and `, modified` when `modified: true`). The citation is `<<key>>`, or, when the source gives an
`iri`, `<<key, key, iri[label]>>`: the ontology term's address as a link inside the citation, which is how the Connected Systems API
writes it (informative, ISO/IEC Directives Part 2 16.5.10). `mappings` is record-only and never emitted. terms.adoc is written only
when there are term records. A term, alias, definition, note or label containing a closing bracket is refused rather than risk a
malformed entry.

Usage:
  emit.py --records <dir> --out <dir> [--config <ogcspec.gate.toml>]

--config is read only for `namespace`, so that identifiers written in absolute and in relative form compare equal
when dependencies are derived, exactly as in the gate. Without it no namespace is applied.

Writes conformance-classes.adoc, requirements.adoc and abstract-tests.adoc, and terms.adoc when there are term records.
Same input, same bytes.
Exit 0 written; 2 usage error or an unreadable record.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

import yaml

ORDER = ("requirements_class", "requirement", "recommendation", "permission", "abstract_test", "conformance_class", "term")


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


def make_norm(namespace: str):
    """Same as the gate's make_norm: exactly this prefix is stripped from identifiers; nothing is guessed."""
    namespace = (namespace or "").rstrip("/")

    def norm(value):
        if isinstance(value, str) and namespace and value.startswith(namespace + "/"):
            return value[len(namespace):]
        return value

    return norm


def conformance_inherit(records: list[dict], namespace: str = "") -> dict[str, list[str]]:
    """Identical in effect to the gate's conformance_inherit (see there): for each conformance class, by its identifier
    as written, the conformance classes of the requirements classes its own requirements class inherits (in that order),
    then its authored depends_on entries; duplicates and self-references dropped."""
    norm = make_norm(namespace)

    def key(value: object) -> str:
        return norm(value) if isinstance(value, str) else ""

    classes = {key(r.get("id")): r for r in records
               if r.get("kind") == "requirements_class" and key(r.get("id"))}
    by_title = {r["title"]: cid for cid, r in classes.items() if isinstance(r.get("title"), str)}
    conf_for: dict[str, list[str]] = {}
    for r in records:
        if r.get("kind") == "conformance_class" and isinstance(r.get("id"), str):
            conf_for.setdefault(key(r.get("target")), []).append(r["id"])
    out: dict[str, list[str]] = {}
    for r in records:
        if r.get("kind") != "conformance_class" or not isinstance(r.get("id"), str):
            continue
        deps: list[str] = []
        cls = classes.get(key(r.get("target")))
        for entry in (cls.get("inherit") or []) if cls else []:
            entry = str(entry)
            target = by_title.get(entry) or (key(entry) if key(entry) in classes else None)
            if target and len(conf_for.get(target, [])) == 1:
                deps.append(conf_for[target][0])
        deps += [str(d) for d in r.get("depends_on") or []]
        out[r["id"]] = [d for i, d in enumerate(deps) if d != r["id"] and d not in deps[:i]]
    return out


def block(style: str, fields: list[tuple[str, str]], extra: str = "", title: object = None) -> str:
    lines = [style] + ([f".{literal(title)}"] if title else []) + ["====", "[%metadata]"]
    lines += [f"{key}:: {one_line(value)}" for key, value in fields]
    if extra:
        lines.append(extra.rstrip("\n"))
    lines.append("====")
    return "\n".join(lines) + "\n"


def emit_term(r: dict) -> str:
    """One terminological entry. Mirrors the gate's `terms_from_xml`, which reads it back."""
    def bracket_safe(label: str, value: object) -> str:
        text = one_line(value)
        if "]" in text or "\\" in text:
            raise ValueError(f"term {r['id']}: {label} may not contain ']' or a backslash: {text[:60]!r}")
        return text

    name = bracket_safe("term", r.get("term", ""))
    lines = [f"=== pass:c[{name}]"]
    lines += [f"alt:[pass:c[{bracket_safe('alias', a)}]]" for a in r.get("aliases") or []]
    lines += ["", f"pass:c[{bracket_safe('definition', r.get('definition', ''))}]"]
    if r.get("note"):
        lines += ["", f"NOTE: pass:c[{bracket_safe('note', r['note'])}]"]
    if r.get("source"):
        src = {"key": r["source"]} if isinstance(r["source"], str) else dict(r["source"])
        key = one_line(src.get("key", ""))
        if not key or any(c in key for c in " ,<>[]/"):
            raise ValueError(f"term {r['id']}: cannot emit source key {key!r}")
        if src.get("iri"):
            iri = one_line(src["iri"])
            if any(c in iri for c in " <>[],"):
                raise ValueError(f"term {r['id']}: cannot emit source address {iri!r}")
            label = bracket_safe("source label", src.get("label", "")) if src.get("label") else ""
            cite = f"<<{key}, {key}, {iri}[{label}]>>"
        else:
            cite = f"<<{key}>>"
        lines += ["", "[.source]", cite + (", modified" if r.get("modified") else "")]
    return "\n".join(lines) + "\n"


def emit_record(r: dict, dependencies: dict[str, list[str]] | None = None) -> str:
    kind, ident = r["kind"], r["id"]
    if kind == "term":
        return emit_term(r)
    if kind == "requirements_class":
        fields = [("identifier", ident)]
        if r.get("subject"):
            fields.append(("subject", r["subject"]))
        fields += [("inherit", d) for d in r.get("inherit") or []]
        fields += [("requirement", q) for q in r.get("requirements") or []]
        return block("[requirements_class]", fields, title=r.get("title"))
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
        fields = [("identifier", ident)]
        fields += [("inherit", d) for d in (dependencies or {}).get(ident, [])]
        fields += [("target", r.get("target", ""))]
        fields += [("conformance-test", t) for t in r.get("tests") or []]
        return block("[conformance_class]", fields, title=r.get("title"))
    raise ValueError(f"cannot emit kind {kind!r} ({ident!r})")


def emit(records: list[dict], namespace: str = "") -> dict[str, str]:
    for r in records:  # refuse rather than silently drop a record the emitter does not know
        if r.get("kind") not in ORDER or not isinstance(r.get("id"), str):
            raise ValueError(f"cannot emit record with kind {r.get('kind')!r} and id {r.get('id')!r}")
    dependencies = conformance_inherit(records, namespace)

    def part(kinds: tuple[str, ...]) -> str:
        chosen = sorted((r for r in records if r.get("kind") in kinds), key=lambda r: (ORDER.index(r["kind"]), r["id"]))
        return "\n".join(emit_record(r, dependencies) for r in chosen)

    files = {
        "conformance-classes.adoc": part(("conformance_class",)),
        "requirements.adoc": part(("requirements_class", "requirement", "recommendation", "permission")),
        "abstract-tests.adoc": part(("abstract_test",)),
    }
    if any(r.get("kind") == "term" for r in records):
        files["terms.adoc"] = part(("term",))
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Emit Metanorma AsciiDoc from requirement records.")
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--config", type=Path, help="the gate config; only `namespace` is read")
    args = parser.parse_args(argv)
    if not args.records.is_dir():
        print(f"records directory not found: {args.records}", file=sys.stderr)
        return 2
    namespace = ""
    if args.config is not None:
        try:
            namespace = tomllib.loads(args.config.read_text(encoding="utf-8")).get("namespace") or ""
        except (OSError, tomllib.TOMLDecodeError) as error:
            print(f"cannot read config {args.config}: {error}", file=sys.stderr)
            return 2
    try:
        files = emit(load(args.records), namespace)
    except (ValueError, KeyError, yaml.YAMLError) as error:
        print(f"cannot emit: {error}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
