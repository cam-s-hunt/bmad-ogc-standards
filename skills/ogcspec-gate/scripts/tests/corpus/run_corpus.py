#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Run the gate's XML rules over the real-document corpus and print per-rule, per-document counts, plus
the comparison with Metanorma's own MODSPEC messages (an independent check on the extractor).

Usage: run_corpus.py --corpus <root> [--json]
The corpus root must hold the repositories named in corpus.toml with their compiled XML (see that file).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tomllib
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate", HERE.parents[1] / "gate.py")
gate = importlib.util.module_from_spec(spec)
sys.modules["gate"] = gate
spec.loader.exec_module(gate)


def analyse(root: Path, doc: dict) -> dict:
    base = root / doc["dir"]
    xml = base / doc["xml"]
    config = {k: doc[k] for k in ("namespace", "core") if doc.get(k)}
    result: dict = {"name": doc["name"], "status": doc.get("status", "")}
    if not xml.is_file():
        result["error"] = "no compiled XML" + (" (expected: compile fails)" if doc.get("expect_compile_failure") else "")
        result["rules"] = {}
        # run stage 2 against the missing file to show the fail-closed finding
        findings, _, _ = gate.check_xml(xml, [], config, None, None)
        result["rules"] = dict(Counter(f.rule for f in findings if f.rule == "X000"))
        return result
    records, notes = gate.scan_xml(xml)
    findings, not_run = gate.check(records, config)
    findings += gate.annex_findings(xml)
    result.update(records=len(records), notes=notes, not_run=sorted(not_run))
    result["rules"] = dict(Counter(f.rule for f in findings))
    result["findings"] = findings
    messages = gate.messages_from_html(xml.with_suffix(".err.html")) if xml.with_suffix(".err.html").is_file() else []
    result["agreement"] = agreement(findings, messages, records, config)
    return result


def agreement(findings, messages, records, config) -> dict:
    """Compare the extractor and rules with Metanorma's own checks, matched through the element anchor.
    MODSPEC_1 on a requirement (no test) vs M007; MODSPEC_2 on a class (linkage outside the document) vs
    the classes whose inherit entries do not resolve (declared references ignored)."""
    by_anchor = {r.get("_anchor"): r for r in records}
    norm = gate.make_norm(config)
    m1 = {by_anchor[m["ident"]]["id"] for m in messages
          if m["id"] == "MODSPEC_1" and m["ident"] in by_anchor and by_anchor[m["ident"]]["kind"] == "requirement"}
    ours1 = {f.key for f in findings if f.rule == "M007"}
    classes = {r["id"]: r for r in (dict(x, id=norm(x["id"]), inherit=[norm(i) for i in x.get("inherit", [])])
                                    for x in records if x["kind"] == "requirements_class")}
    _, unresolved = gate.dependency_graph(classes, {})
    m2 = {by_anchor[m["ident"]]["id"] for m in messages
          if m["id"] == "MODSPEC_2" and m["ident"] in by_anchor and by_anchor[m["ident"]]["kind"] == "requirements_class"}
    m2 = {norm(x) for x in m2}
    ours2 = set(unresolved)
    return {"MODSPEC_1": len(m1), "M007": len(ours1), "MODSPEC_1_not_M007": sorted(m1 - ours1)[:4],
            "M007_not_MODSPEC_1": sorted(ours1 - m1)[:4],
            "MODSPEC_2": len(m2), "unresolved_inherit": len(ours2), "MODSPEC_2_not_ours": sorted(m2 - ours2)[:4],
            "ours_not_MODSPEC_2": sorted(ours2 - m2)[:4]}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    manifest = tomllib.loads((HERE / "corpus.toml").read_text(encoding="utf-8"))
    results = [analyse(args.corpus, d) for d in manifest["document"]]
    rules = sorted({r for res in results for r in res["rules"]})
    if args.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "findings"} for r in results], indent=2))
        return 0
    names = [r["name"] for r in results]
    print("rule   " + "".join(f"{n:>14}" for n in names))
    print("records" + "".join(f"{r.get('records', '-'):>14}" for r in results))
    for rule in rules:
        print(f"{rule:<7}" + "".join(f"{r['rules'].get(rule, 0):>14}" for r in results))
    for r in results:
        print(f"\n{r['name']}: {r.get('error', '')} notes={r.get('notes')} not_run={r.get('not_run')}")
        if "agreement" in r:
            print("  Metanorma vs gate:", r["agreement"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
