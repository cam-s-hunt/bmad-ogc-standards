#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Record-format experiment (plan step 2): what do the current emitter, Metanorma (pinned image) and gate do with the
fields and kinds that skills/ogcspec-modspec/references/record-format-proposal.md proposes?

One baseline (two requirements/conformance class pairs), one change per variant, plus the worked example file.
For each variant: emit, compile with the pinned image, run the gate with stage 2. Needs the pinned image present locally
(the wrapper never pulls). Results go to <out>/results.json.

Usage:  uv run --with pyyaml python docs/design/record-format-experiment.py <empty-or-scratch-output-dir>
Run on 2026-11-06 with the image in METANORMA-PIN; the observations are in the proposal, section 7.

The "before" observations were made against the tools at commit b401284. Run against later commits several variants differ
by design (v3 gives G004, v4 and v7 give G002, v5a/v5b give X003 because the hand patch now duplicates a line the emitter
writes, v2 emits the title); section 7 lists both. The config puts `core` before the [[normative_references]] table: keys
after a table belong to it (the first run had them inside it, so `core` was not configured; a rerun gave the same results).
"""
import copy, importlib.util, json, subprocess, sys, tempfile, shutil
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
T = load("t_emit", REPO/"skills/ogcspec-metanorma/scripts/tests/test_emit.py")
emit, gate, wrapper, HEADER, IMAGE = T.emit, T.gate, T.wrapper, T.HEADER, T.IMAGE
CONFIG = 'core = "/req/core"\n' + T.CONFIG  # top-level keys must precede the [[normative_references]] table
OUT = Path(sys.argv[1]); shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)

EXT = [
 {"kind": "requirements_class", "id": "/req/ext", "subject": "Example document", "inherit": ["/req/core"],
  "requirements": ["/req/ext/more"]},
 {"kind": "requirement", "id": "/req/ext/more", "statement": "A document SHALL carry more."},
 {"kind": "abstract_test", "id": "/conf/ext/more", "target": "/req/ext/more", "purpose": "Verify more.",
  "steps": ["Check for more."]},
 {"kind": "conformance_class", "id": "/conf/ext", "target": "/req/ext", "tests": ["/conf/ext/more"]},
]
BASE = copy.deepcopy(T.RECORDS) + copy.deepcopy(EXT)
def by(records, rid): return next(r for r in records if r["id"] == rid)

def v_status(rs):
    for r in rs: r["status"] = "proposed"
    return rs
def v_package(rs):
    by(rs, "/req/core")["uml_package"] = "example::core"; by(rs, "/req/ext")["uml_package"] = "example::ext"
    by(rs, "/req/core")["title"] = "Core"; by(rs, "/conf/core")["title"] = "Core conformance"
    return rs
def v_depends(rs): by(rs, "/conf/ext")["depends_on"] = ["/conf/core"]; return rs
def v_inherit(rs): by(rs, "/conf/ext")["inherit"] = ["/conf/core"]; return rs
def v_profile(rs): rs.append({"kind": "profile", "id": "/prof/example", "conformance_classes": ["/conf/core"]}); return rs
def v_typo(rs): by(rs, "/req/ext")["requirments"] = ["/req/ext/more"]; return rs
def v_crossclass(rs): by(rs, "/conf/ext")["tests"] = ["/conf/ext/more", "/conf/core/valid-document"]; return rs
def patch_inherit(files):
    t = files["conformance-classes.adoc"]
    marker = "identifier:: /conf/ext\n"; assert t.count(marker) == 1
    files["conformance-classes.adoc"] = t.replace(marker, marker + "inherit:: /conf/core\n")
    return files

VARIANTS = [
 ("v0_baseline", lambda r: r, None, "layout_list"),
 ("v1_status_everywhere", v_status, None, "layout_list"),
 ("v2_uml_package_and_title", v_package, None, "layout_list"),
 ("v3_conf_depends_on_yaml_only", v_depends, None, "layout_list"),
 ("v4_conf_inherit_yaml_only", v_inherit, None, "layout_list"),
 ("v5a_conf_inherit_in_adoc_only", lambda r: r, patch_inherit, "layout_list"),
 ("v5b_conf_inherit_in_yaml_and_adoc", v_inherit, patch_inherit, "layout_list"),
 ("v6_unknown_kind_profile", v_profile, None, "layout_list"),
 ("v7_misspelled_field", v_typo, None, "layout_list"),
 ("v8_cross_class_test_listed", v_crossclass, None, "layout_list"),
 ("v9_one_record_per_file", lambda r: r, None, "layout_split"),
 ("v11_worked_example_file", None, None, "layout_example"),
 ("v10_duplicate_id_across_files", lambda r: r + [copy.deepcopy(by(r, "/req/ext/more"))], None, "layout_split"),
]
EXAMPLE = REPO / "skills/ogcspec-modspec/references/record-format-example.yaml"
EXAMPLE_CONFIG = "\n".join([
    'records_dir = "records"', 'core = "/req/core"', "[[normative_references]]",
    'name = "Example dependency"', 'uri_prefix = "https://example.org/spec/dep/1.0/"', ""])
results = {}
base_bytes = None
for name, tf, patch, layout in VARIANTS:
    root = OUT/name; (root/"records").mkdir(parents=True); (root/"build").mkdir()
    rs = tf(copy.deepcopy(BASE)) if tf else yaml.safe_load(EXAMPLE.read_text())
    if layout in ("layout_list", "layout_example"):
        (root/"records"/"all.yaml").write_text(yaml.safe_dump(rs, sort_keys=False))
    else:
        for i, r in enumerate(rs): (root/"records"/f"{i:02d}.yaml").write_text(yaml.safe_dump(r, sort_keys=False))
    (root/"ogcspec.gate.toml").write_text(EXAMPLE_CONFIG if layout == "layout_example" else CONFIG)
    res = {"layout": layout}
    try:
        files = emit.emit(load_ := emit.load(root/"records"))
    except Exception as e:
        res["emit"] = f"REFUSED: {type(e).__name__}: {e}"
        # what the gate says without a compile
        code, summ = gate.run(root/"ogcspec.gate.toml", None)
        res["gate_records_only"] = sorted(f"{f['rule']}:{f['key']}" for f in summ["findings"])
        results[name] = res; print(name, res["emit"], flush=True); continue
    res["emit"] = "ok"
    if patch: files = patch(files)
    for fn, text in files.items(): (root/"build"/fn).write_text(text)
    (root/"build"/"doc.adoc").write_text(HEADER)
    blob = json.dumps(files, sort_keys=True)
    if name == "v0_baseline": base_bytes = files
    res["emitted_bytes_equal_baseline"] = (files == base_bytes)
    res["emitted_diff_files"] = [k for k in files if base_bytes and files[k] != base_bytes[k]]
    proc = subprocess.run([sys.executable, str(REPO/"skills/ogcspec-metanorma/scripts/metanorma.py"), "--image", IMAGE,
                           "--adoc", str(root/"build"/"doc.adoc"), "--formats", "xml"], capture_output=True, text=True)
    (root/"build"/"compile.json").write_text(proc.stdout or "{}")
    res["compile_exit"] = proc.returncode
    code, summ = gate.run(root/"ogcspec.gate.toml", None, root/"build"/"doc.xml", root/"build"/"compile.json", root/"build"/"doc.err.html")
    res["gate_exit"] = code
    fnd = summ["findings"]
    res["findings_non_x010"] = sorted(f"{f['rule']}:{f['key']}" for f in fnd if f["rule"] != "X010")
    res["x010_keys"] = sorted(f["key"] for f in fnd if f["rule"] == "X010")
    results[name] = res; print(name, res["emit"], "compile", res["compile_exit"], res["findings_non_x010"], flush=True)
(OUT/"results.json").write_text(json.dumps(results, indent=1))
