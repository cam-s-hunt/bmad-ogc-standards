#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Step 3 prerequisite compiles: (1) how does the pinned Metanorma image carry a class title, and (2) can a profile
(ModSpec Req 19: a union of conformance classes) be written with the existing block types?

Same harness as record-format-experiment.py: emit, compile with the pinned image (offline), gate with stage 2. Hand-patches
the emitted AsciiDoc to show what a changed emitter would write. Results: <out>/results.json.

Usage:  uv run --with pyyaml python docs/design/step3-compile-tests.py <scratch-output-dir>

A probe made before step 3 was implemented, against the tools at b401284 (run 2026-11-06). Run it against later commits and
the profile variant duplicates the inherit lines the emitter now writes itself; the title variants then also differ.
"""
import copy, importlib.util, json, subprocess, sys, shutil
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
T = load("t_emit", REPO/"skills/ogcspec-metanorma/scripts/tests/test_emit.py")
emit, gate, HEADER, IMAGE = T.emit, T.gate, T.HEADER, T.IMAGE
CONFIG = 'core = "/req/core"\n' + T.CONFIG  # top-level keys must precede the [[normative_references]] table
OUT = Path(sys.argv[1]); shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)

EXT = [
 {"kind": "requirements_class", "id": "/req/ext", "subject": "Example document", "inherit": ["/req/core"], "requirements": ["/req/ext/more"]},
 {"kind": "requirement", "id": "/req/ext/more", "statement": "A document SHALL carry more."},
 {"kind": "abstract_test", "id": "/conf/ext/more", "target": "/req/ext/more", "purpose": "Verify more.", "steps": ["Check for more."]},
 {"kind": "conformance_class", "id": "/conf/ext", "target": "/req/ext", "tests": ["/conf/ext/more"]},
]
BASE = copy.deepcopy(T.RECORDS) + copy.deepcopy(EXT)
def by(rs, rid): return next(r for r in rs if r["id"] == rid)

def titled(title_req, title_conf):
    def transform(rs):
        by(rs, "/req/core")["title"] = title_req; by(rs, "/conf/core")["title"] = title_conf; return rs
    def patch(files):
        a = files["requirements.adoc"]; m = "[requirements_class]\n====\n[%metadata]\nidentifier:: /req/core\n"
        assert a.count(m) == 1; files["requirements.adoc"] = a.replace(m, m.replace("\n====", f"\n.{title_req}\n===="), 1)
        c = files["conformance-classes.adoc"]; m = "[conformance_class]\n====\n[%metadata]\nidentifier:: /conf/core\n"
        assert c.count(m) == 1; files["conformance-classes.adoc"] = c.replace(m, m.replace("\n====", f"\n.{title_conf}\n===="), 1)
        return files
    return transform, patch

def profile(rs):
    rs += [{"kind": "requirements_class", "id": "/req/prof", "subject": "Example document", "inherit": ["/req/core", "/req/ext"], "requirements": []},
           {"kind": "conformance_class", "id": "/conf/prof", "target": "/req/prof", "inherit": ["/conf/core", "/conf/ext"], "tests": []}]
    return rs
def profile_patch(files):
    t = files["conformance-classes.adoc"]; m = "identifier:: /conf/prof\n"; assert t.count(m) == 1
    files["conformance-classes.adoc"] = t.replace(m, m + "inherit:: /conf/core\ninherit:: /conf/ext\n"); return files

tr, tp = titled("Core", "Core conformance")
mr, mp = titled("Core *bold* _under_ {name} -- 'q' <<x>>", "Core conformance")
lr, lp = titled("pass:c[Core *bold* _under_ {name} -- 'q' <<x>>]", "Core conformance")
VARIANTS = [
 ("t0_baseline", lambda r: r, None),
 ("t1_title_as_block_title", tr, tp),
 ("t2_title_with_markup_plain", mr, mp),
 ("t3_title_with_markup_passthrough", lr, lp),
 ("p1_profile_from_existing_kinds", profile, profile_patch),
]
results = {}
for name, tf, patch in VARIANTS:
    root = OUT/name; (root/"records").mkdir(parents=True); (root/"build").mkdir()
    rs = tf(copy.deepcopy(BASE))
    (root/"records"/"all.yaml").write_text(yaml.safe_dump(rs, sort_keys=False)); (root/"ogcspec.gate.toml").write_text(CONFIG)
    files = emit.emit(emit.load(root/"records"))
    if patch: files = patch(files)
    for fn, text in files.items(): (root/"build"/fn).write_text(text)
    (root/"build"/"doc.adoc").write_text(HEADER)
    proc = subprocess.run([sys.executable, str(REPO/"skills/ogcspec-metanorma/scripts/metanorma.py"), "--image", IMAGE,
                           "--adoc", str(root/"build"/"doc.adoc"), "--formats", "xml"], capture_output=True, text=True)
    (root/"build"/"compile.json").write_text(proc.stdout or "{}")
    res = {"compile_exit": proc.returncode}
    code, summ = gate.run(root/"ogcspec.gate.toml", None, root/"build"/"doc.xml", root/"build"/"compile.json", root/"build"/"doc.err.html")
    res["findings_non_x010"] = sorted(f"{f['rule']}:{f['key']}" for f in summ["findings"] if f["rule"] != "X010")
    res["x010_keys"] = sorted(f["key"] for f in summ["findings"] if f["rule"] == "X010")
    if (root/"build"/"doc.xml").is_file():
        xr = gate.records_from_xml(root/"build"/"doc.xml")
        res["xml_titles"] = {r["id"]: r.get("title") for r in xr if r["kind"] in ("requirements_class", "conformance_class") and "title" in r}
        res["xml_profile"] = {r["id"]: {k: r.get(k) for k in ("inherit", "requirements", "tests", "subject", "target")} for r in xr if r["id"] in ("/req/prof", "/conf/prof")}
    results[name] = res; print(name, json.dumps({k: v for k, v in res.items() if k != "x010_keys"}), flush=True)
(OUT/"results.json").write_text(json.dumps(results, indent=1))
