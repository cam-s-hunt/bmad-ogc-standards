#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""gate: check ModSpec requirement records, and the Metanorma document compiled from them.

This is the canonical copy of the rule engine. The standard's repository vendors a released copy of
this file into its own CI; it must not be re-implemented elsewhere.

Rules are a table (RULES below). Each rule has an ID, a BASIS and the text it rests on:
  M*  spec    a requirement of ModSpec Part 1 (OGC 08-131r7), cited by requirement number
  P*  policy  the ModSpec Policy (OGC 25-001, a DRAFT at the time of writing)
  S*  style   a house convention; not required by any OGC document; runs only if `style` enables it
  X*  stage 2 about the compiled document and the compile itself
  G001        record structure
A rule whose text could not be read is not in the default set. Severity thresholds are deliberately
absent: a finding is a finding, and a known finding is accepted only through an explicit baseline.
Where a requirement admits two readings the rule implements the literal one and says so in its clause.

Record files: YAML under `records_dir`, each file one mapping or a list of mappings with a `kind`:
  requirements_class  id  subject (the standardization target type), inherit[], requirements[], title (optional;
                      an inherit entry may name a class by its title, as OGC API - Records does), uml_package
                      (optional, record-only), profile (optional boolean: the class is a profile, Req 19)
  requirement         id  statement
  abstract_test       id  target (a requirement id), purpose, steps[] (optional)
  conformance_class   id  target (a requirements class id), tests[], title (optional), depends_on[] (optional:
                      conformance classes OUTSIDE this document; the ones inside are derived from the requirements
                      class's `inherit`, see conformance_inherit)
  recommendation      id  statement   (never needs a test)
  permission          id  statement   (never needs a test)
Any kind may carry `status` (proposed or accepted, record-only). A field outside this table is G002. The rules for
these fields (G002-G004, M013, M014, S003-S005) run on authored YAML records only, never on records rebuilt from
compiled XML, so they cannot fire on an approved OGC document. See ogcspec-modspec/references/record-format-proposal.md.

Config (project-owned TOML, the gate's only configuration surface):
  records_dir   directory of record files, relative to the config file (default "records")
  namespace     the document's URI namespace, e.g. "https://www.opengis.net/spec/modspec-1/1.1". Exactly
                this prefix is stripped from identifiers so `<namespace>/req/core` equals `/req/core`.
                It is never guessed, and http/https or `_`/`-` variants are NOT treated as equal.
  core          identifier of the core requirements class, e.g. "/req/core" (enables M011, M012)
  core_dependency  "direct" (default, the literal text of Req 22) or "transitive" (a chain through other classes
                is accepted; a class that never reaches the core is still reported)
  style         list of house-style rule groups to run: "prefix" (S001, S002), "uml" (S003, S004), "layout" (S005)
                (default none)
  [verbal_forms]  optional override of the forms P002 looks for, per kind. Default: the preferred forms of
                ISO/IEC Directives Part 2 (ed. 9.0, 2021-05) clause 7, matched ignoring case. Set
                `iso_verbal_forms = false` to turn P002/P003 off.
  [[normative_references]]  name, uri_prefix: external inherit targets match a prefix or a name. If none are
                declared, only relative inherit targets (starting "/") are checked by M009.

Usage:
  gate.py --config <toml> [--baseline <json>] [--write-baseline <json>]
          [--xml <doc.xml> [--compile-result <json>] [--messages <doc.err.html>]]

Stage 2 (--xml) reads the semantic XML Metanorma compiled from the records, rebuilds record dicts from
it, runs the same rules (finding keys prefixed "xml:"), compares XML records to YAML records field by
field (X001-X003), reports a compiled document with no definitions (X004: table-style requirements,
as in OGC API - Features Part 1, are deliberately NOT parsed: this project defines its own requirement format), checks the test annex is normative (P001), and turns
each Metanorma log message into a finding (X010). A compile that failed is X000 and never reads as
"zero records".

Output: one JSON object on stdout {"records", "findings", "rules_run", "rules_not_run", "notes",
"baseline"}. Exit 0 when the findings equal the baseline (or there are none), 1 otherwise, 2 on a
usage error.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape
from pathlib import Path

import yaml

NAME = r"[a-z0-9][a-z0-9-]*"
STYLE_ID_PATTERNS = {
    "requirements_class": re.compile(rf"^/req/{NAME}$"),
    "requirement": re.compile(rf"^/req/{NAME}/{NAME}$"),
    "abstract_test": re.compile(rf"^/conf/{NAME}/{NAME}$"),
    "conformance_class": re.compile(rf"^/conf/{NAME}$"),
    "recommendation": re.compile(rf"^/rec/{NAME}/{NAME}$"),
    "permission": re.compile(rf"^/per/{NAME}/{NAME}$"),
}
KINDS = tuple(STYLE_ID_PATTERNS)
STATUS_VALUES = ("proposed", "accepted")
COMMON_FIELDS = frozenset({"kind", "id", "status"})
KNOWN_FIELDS = {
    "requirements_class": frozenset({"subject", "inherit", "requirements", "title", "uml_package", "profile"}),
    "requirement": frozenset({"statement"}),
    "recommendation": frozenset({"statement"}),
    "permission": frozenset({"statement"}),
    "abstract_test": frozenset({"target", "purpose", "steps"}),
    "conformance_class": frozenset({"target", "tests", "title", "depends_on"}),
}
FIELD_HINTS = {
    ("conformance_class", "inherit"): "a conformance class's dependencies inside this document are derived from its "
                                      "requirements class's `inherit`; write only dependencies outside the document as `depends_on`",
}
EXTERNAL = re.compile(r"^https?://")
# ISO/IEC Directives Part 2 ed. 9.0 (2021-05), clause 7, preferred forms (first column of Tables 3-5), singular.
ISO_VERBAL_FORMS = {"requirement": ["shall", "shall not"], "recommendation": ["should", "should not"],
                    "permission": ["may"]}
FORBIDDEN_FORMS = ("must", "may not")

# rule id -> (description, basis, source text). Spec rules cite the numbered requirement of 08-131r7
# (the "Requirement N" labels in its clause 8) and were read against the source text on 2026-11-06.
RULES = {
    "G001": ("record has a known kind", "structure", "record structure"),
    "G002": ("a record carries only fields known for its kind", "structure",
             "record-format-proposal.md section 11: an unknown or misspelled field is otherwise ignored silently"),
    "G003": ("field values have the expected type and value (status, profile, uml_package, title, depends_on)", "structure",
             "record-format-proposal.md section 3"),
    "G004": ("depends_on names only conformance classes outside this document", "structure",
             "record-format-proposal.md section 4: dependencies inside the document are derived from `inherit`, "
             "so authoring them would give two sources of truth"),
    "M001": ("every component has an identifier, and identifiers are unique", "spec",
             "08-131r7 Req 2 (/req/core/all-components-assigned-uri)"),
    "M002": ("each requirement is listed by exactly one requirements class", "spec",
             "08-131r7 Req 28 (/req/core/reqs-are-in-class), ATS 15; literal reading: 'listed by' is membership"),
    "M003": ("every requirement a class lists is defined in the document", "spec",
             "08-131r7 Req 28; a listed-but-undefined requirement has no home"),
    "M004": ("each requirements class names a single standardization target type", "spec",
             "08-131r7 Req 4 (/req/core/single-standardization-target-type)"),
    "M005": ("requirements classes and conformance classes correspond one-to-one", "spec",
             "08-131r7 Req 8 (/req/core/requirements-class-correspondence-to-conformance-classes)"),
    "M006": ("a conformance class tests all requirements of its requirements class, and only those", "spec",
             "08-131r7 Req 15 (/req/core/conf-class-test-req-class) and Req 11 (conf-class-single-req-class)"),
    "M007": ("each requirement has at least one abstract test", "spec",
             "08-131r7 Req 1 (reqs-are-testable) and clause 8.5: without a test 'it cannot be considered a requirement'"),
    "M008": ("each abstract test targets a requirement defined in the document", "spec",
             "08-131r7 clause 6.3: a test refers to its requirement by identifier"),
    "M009": ("inherit targets are classes of this document or declared normative references", "spec",
             "08-131r7 Req 12 (con-class-dependencies): a dependency that cannot be resolved cannot be tested"),
    "M010": ("requirements classes do not depend on each other in a cycle", "spec",
             "08-131r7 Req 16 (co-dependent-requirements): co-dependent classes SHALL be merged"),
    "M011": ("the configured core requirements class is defined", "spec",
             "08-131r7 Req 20 (core-requirements-separate)"),
    "M012": ("every class other than the core inherits the core directly", "spec",
             "08-131r7 Req 22 B (req-class-not-core-stt-subtype-of-core); default is the literal reading (the core is in the "
             "class's own dependency list); `core_dependency = \"transitive\"` accepts a chain. Open question for the "
             "ModSpec maintainers; see docs/research/Req22-transitive-dependency.md"),
    "M013": ("a profile has no requirements or tests of its own and builds on at least one class", "spec",
             "08-131r7 Req 19 (/req/core/profile-conformance): a profile's tests are the union of a list of conformance "
             "classes. 'No tests of its own' is that reading; 'no requirements of its own' is inferred (Req 1 / M007: a "
             "requirement needs a test). The `profile` marker is this project's design (proposal section 9)"),
    "M014": ("a conformance class's depends_on entries resolve to a relative id or a declared normative reference", "spec",
             "08-131r7 Req 12 (/req/core/con-class-dependencies): a dependency that cannot be resolved cannot be tested; "
             "ATS 12 is 'inspect the document', so whether the dependency is used to test is not checked"),
    "P001": ("abstract tests are in a normative annex", "policy",
             "25-001 (draft): the Abstract Test Suite annex SHALL be designated normative"),
    "P002": ("a provision contains the preferred verbal form for its kind", "policy",
             "25-001 (draft) -> ISO/IEC Directives Part 2 ed. 9.0 (2021-05) cl. 7, Tables 3-5: shall / should / may; "
             "case is not addressed there, so matching ignores case"),
    "P003": ("a provision does not use 'must' or 'may not'", "policy",
             "ISO/IEC Directives Part 2 ed. 9.0 cl. 7.2: 'Do not use \"must\" as an alternative for \"shall\"' and "
             "'Do not use \"may not\" instead of \"shall not\"'; 'must' is reserved for external constraints (7.6)"),
    "S001": ("identifier matches the project's pattern for its kind", "style", "house style; not an OGC requirement"),
    "S002": ("a requirement's identifier prefix is its class's identifier", "style", "house style; not an OGC requirement"),
    "S003": ("every requirements class names a uml_package", "style", "project convention for ModSpec Part 2 (which defines no notation); not required by any OGC document"),
    "S004": ("no two requirements classes name the same uml_package", "style", "ModSpec Part 2 REQ005: each class is associated to a unique package; read via the digest"),
    "S005": ("a record is alone in a file whose path follows its identifier", "style", "project layout convention; not required by any OGC document"),
    "X000": ("the compile produced a usable semantic XML document", "stage2", "fail closed: an aborted compile is not zero records"),
    "X001": ("every YAML record appears in the compiled XML", "stage2", "emitter and compiler fidelity"),
    "X002": ("every compiled record comes from a YAML record", "stage2", "emitter and compiler fidelity"),
    "X003": ("a record's fields in the XML equal its YAML fields", "stage2", "emitter and compiler fidelity"),
    "X004": ("the compiled document contains requirement definitions", "stage2", "fail closed: table-style markup compiles to none"),
    "X010": ("Metanorma log message (accepted only through the baseline)", "stage2", "Metanorma log; severity is carried in the message"),
}
SPEC_RULES = tuple(r for r in RULES if r.startswith(("M", "P")))


@dataclass(frozen=True)
class Finding:
    rule: str
    key: str
    message: str

    def as_dict(self) -> dict:
        return {"rule": self.rule, "key": self.key, "message": self.message,
                "basis": RULES[self.rule][1], "clause": RULES[self.rule][2]}

    @property
    def ident(self) -> str:
        return f"{self.rule}:{self.key}"


def load_records(directory: Path) -> tuple[list[dict], list[Finding]]:
    records: list[dict] = []
    findings: list[Finding] = []
    for path in sorted(directory.rglob("*.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            findings.append(Finding("G001", path.name, f"YAML does not parse: {error}"))
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                findings.append(Finding("G001", path.name, "record is not a mapping"))
                continue
            item["_file"] = path.name
            item["_path"] = path.relative_to(directory).as_posix()
            records.append(item)
    return records, findings


def make_norm(config: dict):
    namespace = (config.get("namespace") or "").rstrip("/")

    def norm(value):
        if isinstance(value, str) and namespace and value.startswith(namespace + "/"):
            return value[len(namespace):]
        return value

    return norm


def field_findings(records: list[dict]) -> list[Finding]:
    """G002 (fields outside the table for the kind) and G003 (wrong type or value), on authored records only."""
    out: list[Finding] = []
    for r in records:
        kind = r.get("kind")
        if kind not in KINDS:
            continue
        ident = r["id"] if isinstance(r.get("id"), str) and r["id"] else r.get("_file", "?")
        allowed = COMMON_FIELDS | KNOWN_FIELDS[kind]
        for field in sorted(str(k) for k in r if not str(k).startswith("_") and k not in allowed):
            hint = FIELD_HINTS.get((kind, field))
            if hint is None:
                near = difflib.get_close_matches(field, sorted(allowed), n=1)
                hint = f"did you mean {near[0]!r}?" if near else f"known fields: {sorted(allowed)}"
            out.append(Finding("G002", f"{ident}#{field}", f"{kind} has no field {field!r}; {hint}"))
        if "status" in r and r["status"] not in STATUS_VALUES:
            out.append(Finding("G003", f"{ident}#status", f"status {r['status']!r} is not one of {list(STATUS_VALUES)}"))
        if "profile" in r and not isinstance(r["profile"], bool):
            out.append(Finding("G003", f"{ident}#profile", f"profile must be true or false, not {r['profile']!r}"))
        for field in ("uml_package", "title"):
            if field in r and not (isinstance(r[field], str) and r[field].strip()):
                out.append(Finding("G003", f"{ident}#{field}", f"{field} must be a non-empty string, not {r[field]!r}"))
        if "depends_on" in r and not (isinstance(r["depends_on"], list)
                                      and all(isinstance(d, str) and d.strip() for d in r["depends_on"])):
            out.append(Finding("G003", f"{ident}#depends_on", "depends_on must be a list of non-empty identifier strings"))
    return out


def conformance_inherit(records: list[dict], config: dict) -> dict[str, list[str]]:
    """The dependency list each conformance class carries in the document (its `inherit::` lines), by the class's
    identifier as written. Derived entries come first, in the order of the requirements class's `inherit`: for each
    entry that names a requirements class of this document (by identifier, or by title), the identifier of that class's
    one conformance class (Req 8). Then the authored `depends_on` entries. Duplicates and self-references are dropped.
    ogcspec-metanorma/scripts/emit.py holds an identical copy for the emitter; a test keeps the two equal, and
    stage 2 (X003) compares the result with the compiled document."""
    norm = make_norm(config)

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


def reach_from(graph: dict[str, set[str]], start: str) -> set[str]:
    seen: set[str] = set()
    stack = list(graph.get(start, ()))
    while stack:
        n = stack.pop()
        if n not in seen:
            seen.add(n)
            stack.extend(graph.get(n, ()))
    return seen


def strongly_connected(graph: dict[str, set[str]]) -> list[list[str]]:
    """Groups of nodes that can all reach each other (including a node that reaches itself)."""
    def reach(start: str) -> set[str]:
        seen: set[str] = set()
        stack = list(graph.get(start, ()))
        while stack:
            n = stack.pop()
            if n not in seen:
                seen.add(n)
                stack.extend(graph.get(n, ()))
        return seen

    reachable = {n: reach(n) for n in graph}
    groups, done = [], set()
    for n in sorted(graph):
        if n in done or n not in reachable[n]:
            continue
        group = sorted(m for m in graph if m in reachable[n] and n in reachable[m])
        done.update(group)
        groups.append(group)
    return groups


def dependency_graph(classes: dict[str, dict], config: dict) -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    """Edges between classes of this document, and the inherit entries that resolve to none of them and are
    not declared normative references. An entry resolves by class identifier or by class title (OGC API -
    Records names its dependencies by title)."""
    refs = config.get("normative_references", [])
    prefixes = [ref["uri_prefix"] for ref in refs if ref.get("uri_prefix")]
    names = {ref["name"] for ref in refs if ref.get("name")}
    by_title = {c["title"]: cid for cid, c in classes.items() if isinstance(c.get("title"), str)}
    graph: dict[str, set[str]] = {cid: set() for cid in classes}
    unresolved: dict[str, list[str]] = {}
    for cid, c in classes.items():
        for dep in map(str, c.get("inherit") or []):
            if dep in by_title:
                graph[cid].add(by_title[dep])
            elif dep in classes:
                graph[cid].add(dep)
            elif dep in names or (EXTERNAL.match(dep) and any(dep.startswith(p) for p in prefixes)):
                continue
            else:
                unresolved.setdefault(cid, []).append(dep)
    return graph, unresolved


def check(records: list[dict], config: dict, authored: bool = False) -> tuple[list[Finding], dict[str, str]]:
    """Run the record rules. Returns (findings, rules_not_run: id -> reason). `authored` is true for YAML records
    the project writes (see `run`), false for records rebuilt from compiled XML; the rules about fields only an
    author can write (G002-G004, M013, M014, S003-S005) run only on authored records."""
    out: list[Finding] = []
    not_run: dict[str, str] = {}
    norm = make_norm(config)
    style = set(config.get("style") or [])
    if authored:
        out += field_findings(records)
    else:
        for rule in ("G002", "G003", "G004", "M013", "M014", "S003", "S004", "S005"):
            not_run[rule] = "applies to authored YAML records only"
    valid: list[dict] = []
    for r in records:
        kind = r.get("kind")
        rid = norm(r.get("id")) if isinstance(r.get("id"), str) and r.get("id") else None
        r = {**r, "id": rid}
        for f in ("target",):
            if isinstance(r.get(f), str):
                r[f] = norm(r[f])
        for f in ("inherit", "requirements", "tests", "depends_on"):
            if isinstance(r.get(f), list):
                r[f] = [norm(x) for x in r[f]]
        if kind not in KINDS:
            out.append(Finding("G001", rid or r.get("_anchor") or r.get("_file", "?"), f"unknown kind {kind!r}"))
            continue
        if not rid:
            out.append(Finding("M001", r.get("_anchor") or r.get("_file", "?"), f"{kind} has no identifier"))
            continue
        valid.append(r)

    seen: dict[str, int] = {}
    for r in valid:
        seen[r["id"]] = seen.get(r["id"], 0) + 1
    out += [Finding("M001", i, f"identifier used by {n} records") for i, n in sorted(seen.items()) if n > 1]

    by_kind = {k: {r["id"]: r for r in valid if r["kind"] == k} for k in KINDS}
    classes, reqs, tests = by_kind["requirements_class"], by_kind["requirement"], by_kind["abstract_test"]
    confs = by_kind["conformance_class"]

    listers: dict[str, list[str]] = {}
    for cid, c in classes.items():
        for rid in c.get("requirements") or []:
            listers.setdefault(rid, []).append(cid)
    for rid in reqs:
        n = len(listers.get(rid, []))
        if n != 1:
            out.append(Finding("M002", rid, f"listed by {n} requirements classes (expected exactly 1)"
                               + (f": {sorted(listers[rid])}" if n else "")))
    for cid, c in classes.items():
        for rid in c.get("requirements") or []:
            if rid not in reqs:
                out.append(Finding("M003", f"{cid}>{rid}", f"{cid} lists {rid}, which is not defined as a requirement"))
        subject = c.get("subject")
        if not isinstance(subject, str) or not subject.strip():
            out.append(Finding("M004", cid, "no single standardization target type (subject) declared"))

    tested: dict[str, list[str]] = {}
    for tid, t in tests.items():
        target = t.get("target")
        if target not in reqs:
            out.append(Finding("M008", tid, f"target {target!r} is not a requirement defined in the document"))
            continue
        tested.setdefault(target, []).append(tid)
    for rid in reqs:
        if rid not in tested:
            out.append(Finding("M007", rid, "no abstract test targets this requirement"))

    conf_for: dict[str, list[str]] = {}
    for cid, c in confs.items():
        target = c.get("target")
        if target not in classes:
            out.append(Finding("M005", cid, f"target {target!r} is not a requirements class of the document"))
            continue
        conf_for.setdefault(target, []).append(cid)
        listed = c.get("tests") or []
        members = {r for r in reqs if target in listers.get(r, [])}
        for t in listed:
            if t not in tests:
                out.append(Finding("M006", f"{cid}>{t}", f"{cid} lists {t}, which is not a defined abstract test"))
            elif tests[t].get("target") in reqs and tests[t]["target"] not in members:
                out.append(Finding("M006", f"{cid}>{t}", f"{t} tests {tests[t]['target']}, which is not a requirement of {target}"))
        covered = {tests[t].get("target") for t in listed if t in tests}
        uncovered = sorted(members - covered)
        if uncovered:  # one finding per conformance class: one wrong link can leave hundreds of requirements uncovered
            out.append(Finding("M006", f"{cid}>uncovered:{len(uncovered)}",
                               f"{cid} lists no abstract test for {len(uncovered)} requirements of {target}, "
                               f"first: {uncovered[:5]}"))
    for cid in classes:
        n = len(conf_for.get(cid, []))
        if n != 1:
            out.append(Finding("M005", cid, f"{n} conformance classes target this requirements class (expected 1)"))

    graph, unresolved = dependency_graph(classes, config)
    declared = bool(config.get("normative_references"))
    for cid, deps in sorted(unresolved.items()):
        for dep in deps:
            if dep.startswith("/") or declared:  # a relative id must resolve; external ones only if the project declares them
                what = "inherit target is not a class of this document" if dep.startswith("/") else \
                    "inherit target matches no declared normative reference"
                out.append(Finding("M009", f"{cid}>{dep}", f"{cid}: {what}: {dep}"))
    for group in strongly_connected(graph):
        out.append(Finding("M010", "+".join(group), f"requirements classes depend on each other: {group}"))

    core = norm(config.get("core")) if config.get("core") else None
    if core:
        if core not in classes:
            out.append(Finding("M011", core, f"configured core class {core} is not defined"))
        else:
            mode = config.get("core_dependency", "direct")
            for cid in classes:
                if cid == core or core in graph[cid]:
                    continue
                reachable = core in reach_from(graph, cid)
                if reachable and mode == "transitive":
                    continue
                state = "transitive" if reachable else "unreachable"
                out.append(Finding("M012", f"{cid}>{state}",
                                   f"{cid} does not list {core} among its direct dependencies; "
                                   + ("it reaches the core only through other classes" if reachable
                                      else "it does not reach the core at all")))
    else:
        not_run["M011"] = not_run["M012"] = "no `core` configured"

    if authored:
        refs = config.get("normative_references", [])
        prefixes = [ref["uri_prefix"] for ref in refs if ref.get("uri_prefix")]
        names = {ref["name"] for ref in refs if ref.get("name")}
        for cid, c in confs.items():
            for dep in c.get("depends_on") or []:
                if not isinstance(dep, str):
                    continue  # G003
                if dep in confs:
                    out.append(Finding("G004", f"{cid}>{dep}",
                                       f"{cid} lists {dep}, a conformance class of this document, in depends_on; "
                                       "it is derived from the requirements class's inherit, so remove it"))
                elif dep.startswith("/"):
                    out.append(Finding("M014", f"{cid}>{dep}", f"{cid}: depends_on target is not a conformance class of this document: {dep}"))
                elif refs and not (dep in names or (EXTERNAL.match(dep) and any(dep.startswith(p) for p in prefixes))):
                    out.append(Finding("M014", f"{cid}>{dep}", f"{cid}: depends_on target matches no declared normative reference: {dep}"))
        for cid, c in classes.items():
            if c.get("profile") is not True:
                continue
            if c.get("requirements"):
                out.append(Finding("M013", f"{cid}>requirements", f"profile {cid} lists requirements of its own"))
            for conf in conf_for.get(cid, []):
                if confs[conf].get("tests"):
                    out.append(Finding("M013", f"{cid}>tests", f"the conformance class {conf} of profile {cid} lists tests of its own"))
            if not c.get("inherit"):
                out.append(Finding("M013", f"{cid}>inherit", f"profile {cid} builds on no class (its inherit list is empty)"))

    if config.get("iso_verbal_forms", True) is False and not config.get("verbal_forms"):
        not_run["P002"] = not_run["P003"] = "iso_verbal_forms = false and no [verbal_forms] configured"
    else:
        forms = config.get("verbal_forms") or ISO_VERBAL_FORMS
        for kind, table in (("requirement", reqs), ("recommendation", by_kind["recommendation"]),
                            ("permission", by_kind["permission"])):
            wanted = forms.get(kind) or []
            for rid, r in table.items():
                text = r.get("statement")
                if not isinstance(text, str) or not text.strip():
                    out.append(Finding("P002", rid, "statement is missing or empty"))
                    continue
                if wanted and not any(re.search(rf"\b{re.escape(w)}\b", text, re.I) for w in wanted):
                    out.append(Finding("P002", rid, f"{kind} text contains none of {wanted}"))
                for bad in FORBIDDEN_FORMS:
                    if re.search(rf"\b{re.escape(bad)}\b", text, re.I):
                        out.append(Finding("P003", f"{rid}#{bad}", f"{kind} text uses {bad!r}"))

    if "prefix" in style:
        for r in valid:
            if not STYLE_ID_PATTERNS[r["kind"]].match(r["id"]):
                out.append(Finding("S001", r["id"], f"{r['kind']} id does not match {STYLE_ID_PATTERNS[r['kind']].pattern}"))
        for rid in reqs:
            for cid in listers.get(rid, []):
                if not rid.startswith(cid + "/"):
                    out.append(Finding("S002", rid, f"listed by {cid} but its identifier does not start with {cid}/"))
    else:
        not_run["S001"] = not_run["S002"] = "style group 'prefix' not enabled"
    if authored:
        if "uml" in style:
            packages: dict[str, list[str]] = {}
            for cid, c in classes.items():
                package = c.get("uml_package")
                if not isinstance(package, str) or not package.strip():
                    out.append(Finding("S003", cid, f"requirements class {cid} names no uml_package"))
                else:
                    packages.setdefault(package, []).append(cid)
            out += [Finding("S004", package, f"uml_package {package!r} is named by {sorted(ids)}")
                    for package, ids in sorted(packages.items()) if len(ids) > 1]
        else:
            not_run["S003"] = not_run["S004"] = "style group 'uml' not enabled"
        if "layout" in style:
            per_file: dict[str, int] = {}
            for r in valid:
                per_file[r.get("_path", "?")] = per_file.get(r.get("_path", "?"), 0) + 1
            for r in valid:
                path = r.get("_path")
                if path is None:
                    continue
                if not r["id"].startswith("/"):
                    out.append(Finding("S005", f"{r['id']}#path", f"{r['id']} is not relative to the namespace, so no path can follow it"))
                elif path not in (r["id"].lstrip("/") + ".yaml", r["id"].lstrip("/") + ".yml"):
                    out.append(Finding("S005", f"{r['id']}#path", f"{r['id']} is in {path}, expected {r['id'].lstrip('/')}.yaml"))
            out += [Finding("S005", f"{path}#records", f"{path} holds {n} records, expected 1")
                    for path, n in sorted(per_file.items()) if n > 1]
        else:
            not_run["S005"] = "style group 'layout' not enabled"
    return out, not_run


# ---------------------------------------------------------------- stage 2: compiled semantic XML

TYPE_TO_KIND = {  # (element local name, requirement type attribute) -> record kind
    ("requirement", "class"): "requirements_class",
    ("requirement", "conformanceclass"): "conformance_class",
    ("requirement", "abstracttest"): "abstract_test",
    ("requirement", None): "requirement",
    ("recommendation", None): "recommendation",
    ("permission", None): "permission",
}
PROVISIONS = {"requirement", "recommendation", "permission"}
TARGET_TYPE_TAGS = {"target-type", "target type"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _raw_text(element: ET.Element) -> str:
    own = (element.text or "") + "".join(_raw_text(c) + (c.tail or "") for c in element)
    if _local(element.tag) == "link" and not own.strip():
        return element.get("target") or ""  # a bare URL compiles to an empty <link target=...>
    return own


def _text(element: ET.Element) -> str:
    return " ".join(_raw_text(element).split())


TYPOGRAPHY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "​": None})


def canon(value: object) -> str:
    """Whitespace-collapse and undo the typography Metanorma applies after the emitter (smart quotes,
    dashes, ellipsis). Anything else that differs is a real change."""
    text = " ".join(str(value or "").translate(TYPOGRAPHY).split())
    return text.replace("—", "--").replace("…", "...")


def _identifier(element: ET.Element) -> str:
    for child in element:
        if _local(child.tag) == "identifier":
            return _text(child)
    return ""


def _inherit_value(element: ET.Element, anchors: dict[str, str]) -> str:
    """An inherit entry written as a cross-reference (`<<rc_record-core,Record Core>>`) names a class by its
    anchor: use that class's identifier. Otherwise the entry's text (an identifier, URI or citation)."""
    xref = next((x for x in element.iter() if _local(x.tag) == "xref"), None)
    if xref is not None and xref.get("target") in anchors:
        return anchors[xref.get("target")]
    return _text(element)


def _description_list(element: ET.Element) -> list[tuple[str, ET.Element]]:
    """Metanorma keeps a class whose `inherit` cites a bibliography item (eref) as a plain definition list inside
    `description` instead of structured fields. Returns its (term, definition) pairs."""
    pairs = []
    for desc in (c for c in element if _local(c.tag) == "description"):
        for dl in (d for d in desc.iter() if _local(d.tag) == "dl"):
            term = None
            for child in dl:
                if _local(child.tag) == "dt":
                    term = _text(child).lower()
                elif _local(child.tag) == "dd" and term:
                    pairs.append((term, child))
    return pairs


def scan_xml(path: Path) -> tuple[list[dict], dict]:
    """Rebuild record dicts from semantic XML. Returns (records, notes).

    A definition is an anchored requirement/recommendation/permission element. The anchor-less nested
    `requirement` elements inside a class are its requirement/test lists, not records. Anchored class and
    conformance-class elements WITHOUT an identifier are shorthand references (OGC API - Processes writes
    `[.conformance_class]` that way); they are counted in notes, not turned into records. A provision
    without an identifier IS a record, and M001 reports it.

    Taken from real documents (ModSpec Part 1, Processes, Records, Connected Systems):
    - statement = the `part` components plus the free-body `description`; `conditions` is excluded.
    - requirements class target type = `subject`, else classification `target-type` / `Target Type`.
    - conformance class -> class link = classification `target`, else `subject` holding an xref to the
      class's anchor (resolved through the anchor map).
    Table-style requirements (OGC API - Features Part 1) compile to no such elements and are not parsed."""
    root = ET.parse(path).getroot()
    anchors = {}
    for e in root.iter():
        if _local(e.tag) in PROVISIONS and e.get("anchor"):
            ident = _identifier(e) or next((_text(dd) for t, dd in _description_list(e) if t == "identifier"), "")
            if ident:
                anchors[e.get("anchor")] = ident
    out: list[dict] = []
    notes = {"shorthand_without_identifier": 0, "unmapped_types": {}}
    for element in root.iter():
        name = _local(element.tag)
        if name not in PROVISIONS or not element.get("anchor"):
            continue
        rtype = element.get("type")
        kind = TYPE_TO_KIND.get((name, rtype))
        ident = _identifier(element)
        if kind is None:
            key = f"{name}/{rtype}"
            notes["unmapped_types"][key] = notes["unmapped_types"].get(key, 0) + 1
            continue
        recovered = None
        if not ident and kind in ("requirements_class", "conformance_class"):
            pairs = _description_list(element)
            ident = next((_text(dd) for t, dd in pairs if t == "identifier"), "")
            if not ident:
                notes["shorthand_without_identifier"] += 1
                continue
            recovered = pairs
            notes["recovered_from_description_list"] = notes.get("recovered_from_description_list", 0) + 1
        record: dict = {"id": ident, "kind": kind, "_file": path.name, "_anchor": element.get("anchor")}
        children = [c for c in element if _local(c.tag) != "identifier"]
        nested = [_identifier(c) for c in children if _local(c.tag) == "requirement" and not c.get("anchor")]
        classes = {}
        for c in children:
            if _local(c.tag) == "classification":
                tag = next((_text(x) for x in c if _local(x.tag) == "tag"), "")
                value = next((_text(x) for x in c if _local(x.tag) == "value"), "")
                classes[tag.lower()] = value
        if recovered is not None and kind == "requirements_class":
            record["subject"] = next((_text(dd) for t, dd in recovered if t == "subject"), None)
            record["inherit"] = [_inherit_value(dd, anchors) for t, dd in recovered if t == "inherit"]
            record["requirements"] = [_text(dd) for t, dd in recovered if t == "requirement"]
            titles = [_text(c) for c in children if _local(c.tag) == "title"]
            if titles:
                record["title"] = titles[0]
            out.append(record)
            continue
        if kind == "requirements_class":
            subjects = [_text(c) for c in children if _local(c.tag) == "subject"]
            fallback = next((v for t, v in classes.items() if t in TARGET_TYPE_TAGS), None)
            record["subject"] = (subjects[0] if subjects else None) or fallback
            record["inherit"] = [_inherit_value(c, anchors) for c in children if _local(c.tag) == "inherit"]
            record["requirements"] = nested
            titles = [_text(c) for c in children if _local(c.tag) == "title"]
            if titles:
                record["title"] = titles[0]
        elif kind == "conformance_class":
            record["tests"] = nested
            record["inherit"] = [_inherit_value(c, anchors) for c in children if _local(c.tag) == "inherit"]
            titles = [_text(c) for c in children if _local(c.tag) == "title"]
            if titles:
                record["title"] = titles[0]
        if kind in ("conformance_class", "abstract_test"):
            target = classes.get("target")
            if not target and kind == "conformance_class":
                for c in children:
                    if _local(c.tag) == "subject":
                        xref = next((x for x in c.iter() if _local(x.tag) == "xref"), None)
                        target = anchors.get(xref.get("target")) if xref is not None else _text(c)
            if target:
                record["target"] = anchors.get(target, target)
        if kind == "abstract_test":
            record["purpose"] = " ".join(_text(c) for c in children
                                         if _local(c.tag) == "component" and c.get("class") == "test-purpose")
            record["steps"] = [_text(step) for c in children
                               if _local(c.tag) == "component" and c.get("class") == "test-method"
                               for step in c.iter() if _local(step.tag) == "component" and step.get("class") == "step"]
        if kind in ("requirement", "recommendation", "permission"):
            parts = [_text(c) for c in children
                     if (_local(c.tag) == "component" and c.get("class") == "part") or _local(c.tag) == "description"]
            record["statement"] = " ".join(p for p in parts if p)
        out.append(record)
    return out, notes


def records_from_xml(path: Path) -> list[dict]:
    return scan_xml(path)[0]


def annex_findings(path: Path) -> list[Finding]:
    """P001: every abstract test sits in an annex designated normative."""
    root = ET.parse(path).getroot()
    out, bad = [], {}
    def walk(node, annex):
        if _local(node.tag) == "annex":
            annex = node
        if _local(node.tag) == "requirement" and node.get("type") == "abstracttest" and node.get("anchor"):
            if annex is None:
                bad.setdefault("(not in an annex)", 0)
                bad["(not in an annex)"] += 1
            elif annex.get("obligation") != "normative":
                key = annex.get("anchor") or annex.get("id") or "annex"
                bad[key] = bad.get(key, 0) + 1
        for c in node:
            walk(c, annex)
    walk(root, None)
    for key, n in sorted(bad.items()):
        out.append(Finding("P001", key, f"{n} abstract tests are not in a normative annex"))
    return out


MESSAGE_ROW = re.compile(r'<tr class="severity(\d)">(.*?)</tr>', re.S)
CELL = re.compile(r"<(?:td|th)[^>]*>(.*?)</(?:td|th)>", re.S)


def messages_from_html(path: Path) -> list[dict]:
    html = path.read_text(encoding="utf-8")
    out = []
    for severity, row in MESSAGE_ROW.findall(html):
        cells = [unescape(re.sub(r"<[^>]+>", "", c)).replace("​", "").replace("­", "").strip()
                 for c in CELL.findall(row)]
        if len(cells) < 6:
            continue
        out.append({"severity": int(severity), "ident": cells[1], "id": cells[2], "message": " ".join(cells[3].split())})
    return out


def message_key(m: dict) -> str:
    where = m["ident"]
    if where in ("", "--"):  # no anchor: fall back to the message with volatile parts removed
        where = re.sub(r"@\d+|[0-9a-f]{8}-[0-9a-f-]{27}", "", m["message"])[:80]
    return f"{m['id']}:{where}"


def check_xml(xml_path: Path, yaml_records: list[dict], config: dict,
              compile_result: Path | None, messages_path: Path | None) -> tuple[list[Finding], dict, dict]:
    out: list[Finding] = []
    abort = xml_path.with_name(xml_path.name + ".abort")
    exit_code: object = 0
    if compile_result is not None:  # only an explicit integer 0 counts as a successful compile
        try:
            exit_code = json.loads(compile_result.read_text(encoding="utf-8")).get("exit")
        except (OSError, ValueError, AttributeError):
            exit_code = "unreadable compile result"
    if messages_path is None:
        messages_path = xml_path.with_suffix(".err.html")
    if messages_path.is_file():
        seen = set()
        for m in messages_from_html(messages_path):
            key = message_key(m)
            if key not in seen:
                seen.add(key)
                out.append(Finding("X010", key, f"severity {m['severity']}: {m['message'][:160]}"))
    compile_ok = exit_code == 0 and not isinstance(exit_code, bool)
    if abort.exists() or not xml_path.is_file() or not compile_ok:
        reasons = [r for r, bad in (("doc.xml.abort present", abort.exists()), ("no XML produced", not xml_path.is_file()),
                                    (f"compile result {exit_code!r}, not 0", not compile_ok)) if bad]
        out.append(Finding("X000", xml_path.name, "; ".join(reasons)))
        return out, {}, {}

    xml_records, notes = scan_xml(xml_path)
    if not xml_records:
        out.append(Finding("X004", xml_path.name, "compiled document has no requirement definitions "
                           "(table-style requirements are not parsed)"))
    found, not_run = check(xml_records, config)
    out += [Finding(f.rule, f"xml:{f.key}", f.message) for f in found]
    out += [Finding(f.rule, f"xml:{f.key}", f.message) for f in annex_findings(xml_path)]

    by_yaml = {(r.get("kind"), r.get("id")): r for r in yaml_records}
    for ident, deps in conformance_inherit(yaml_records, config).items():  # what the emitter writes as inherit::
        if ("conformance_class", ident) in by_yaml:
            by_yaml[("conformance_class", ident)] = {**by_yaml[("conformance_class", ident)], "inherit": deps}
    by_xml = {(r["kind"], r["id"]): r for r in xml_records}
    for key in sorted(set(by_yaml) - set(by_xml), key=str):
        out.append(Finding("X001", f"{key[0]}:{key[1]}", "in the YAML records but not in the compiled XML"))
    for key in sorted(set(by_xml) - set(by_yaml), key=str):
        out.append(Finding("X002", f"{key[0]}:{key[1]}", "in the compiled XML but not in the YAML records"))
    for key in sorted(set(by_yaml) & set(by_xml), key=str):
        a, b = by_yaml[key], by_xml[key]
        for field in ("subject", "target", "statement", "purpose", "title"):
            if field in a or field in b:
                if canon(a.get(field)) != canon(b.get(field)):
                    out.append(Finding("X003", f"{key[1]}#{field}", f"YAML {a.get(field)!r} vs XML {b.get(field)!r}"))
        for field in ("inherit", "requirements", "tests", "steps"):
            if field in a or field in b:
                # steps keep their order (a test method is a sequence); the others are sets
                norm = (lambda v: [canon(x) for x in v or []]) if field == "steps" else (lambda v: sorted(map(str, v or [])))
                if norm(a.get(field)) != norm(b.get(field)):
                    out.append(Finding("X003", f"{key[1]}#{field}", f"YAML {a.get(field)!r} vs XML {b.get(field)!r}"))
    return out, notes, not_run


def run(config_path: Path, baseline_path: Path | None, xml_path: Path | None = None,
        compile_result: Path | None = None, messages_path: Path | None = None) -> tuple[int, dict]:
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    directory = config_path.parent / config.get("records_dir", "records")
    records, findings = load_records(directory)
    found, not_run = check(records, config, authored=True)
    findings += found
    notes: dict = {}
    if xml_path is not None:
        extra, notes, _ = check_xml(xml_path, records, config, compile_result, messages_path)
        findings += extra
    findings.sort(key=lambda f: (f.rule, f.key, f.message))
    idents = {f.ident for f in findings}
    summary: dict = {
        "records": len(records),
        "findings": [f.as_dict() for f in findings],
        "rules_run": sorted(r for r in RULES if r not in not_run and r[0] in "GMPS"),
        "rules_not_run": dict(sorted(not_run.items())),
        "notes": notes,
    }
    if baseline_path is None:
        return (1 if findings else 0), summary
    expected = set(json.loads(baseline_path.read_text(encoding="utf-8")).get("expected", []))
    summary["baseline"] = {"unexpected": sorted(idents - expected), "missing": sorted(expected - idents)}
    return (1 if (idents - expected or expected - idents) else 0), summary


def baseline_problem(path: Path) -> str | None:
    """Why a baseline file cannot be used, or None. A baseline is a JSON object {"expected": [strings]}; anything else
    is a usage error (exit 2), not a crash and not a silent pass."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return f"{path} is not readable JSON ({error})"
    if not isinstance(data, dict) or not isinstance(data.get("expected"), list) or \
            not all(isinstance(x, str) for x in data["expected"]):
        return f'{path} must be a JSON object {{"expected": ["RULE:key", ...]}}'
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check ModSpec requirement records.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--baseline", type=Path, help="accepted findings; any deviation either way fails")
    parser.add_argument("--write-baseline", type=Path, help="write current findings as a baseline and exit 0")
    parser.add_argument("--xml", type=Path, help="compiled semantic XML: also run stage 2")
    parser.add_argument("--compile-result", type=Path, help="JSON from the metanorma wrapper (its exit code is read)")
    parser.add_argument("--messages", type=Path, help="Metanorma .err.html (default: next to the XML)")
    args = parser.parse_args(argv)
    if (args.compile_result or args.messages) and not args.xml:
        print("--compile-result and --messages need --xml", file=sys.stderr)
        return 2
    if not args.config.is_file():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 2
    if args.baseline is not None and not args.baseline.is_file():
        print(f"baseline not found: {args.baseline}", file=sys.stderr)
        return 2
    if args.baseline is not None and not args.write_baseline:
        problem = baseline_problem(args.baseline)
        if problem:
            print(f"baseline unusable: {problem}", file=sys.stderr)
            return 2
    code, summary = run(args.config, args.baseline if not args.write_baseline else None,
                        args.xml, args.compile_result, args.messages)
    if args.write_baseline:
        ids = sorted({f"{f['rule']}:{f['key']}" for f in summary["findings"]})
        args.write_baseline.write_text(json.dumps({"expected": ids}, indent=2) + "\n", encoding="utf-8")
        code = 0
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
