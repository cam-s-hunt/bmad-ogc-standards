"""Emitter tests. The round trip compiles with the pinned Metanorma image and SKIPS (loudly) when the
image is not present locally; a skipped round trip means the emitter's output has not been shown to compile."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[2]
REPO = SKILLS.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


emit = load("emit", HERE.parent / "emit.py")
gate = load("gate", SKILLS / "ogcspec-gate" / "scripts" / "gate.py")
wrapper = load("metanorma_wrapper", HERE.parent / "metanorma.py")

PIN = (REPO / "METANORMA-PIN").read_text(encoding="utf-8") if (REPO / "METANORMA-PIN").is_file() else ""
IMAGE = next((l.split("=", 1)[1].strip() for l in PIN.splitlines() if l.startswith("image=")), "")

D1, D2 = "http://www.opengis.net/spec/example-dep/1.0/conf/core", "http://www.opengis.net/spec/example-dep/1.0/conf/extra"
RECORDS = [
    {"kind": "requirements_class", "id": "/req/core", "subject": "Example document", "inherit": [D1, D2],
     "requirements": ["/req/core/valid-document", "/req/core/stable-ids-listed", "/req/core/special-chars"]},
    {"kind": "requirement", "id": "/req/core/valid-document", "statement": "A document SHALL validate against the schema."},
    {"kind": "requirement", "id": "/req/core/stable-ids-listed", "statement": "A document SHALL list\n  its   identifiers."},
    {"kind": "requirement", "id": "/req/core/special-chars",
     "statement": "A key:: value SHALL be {name} escaped, *bold*, _under_, `code`, ^2^, #mark#, <<xref>>, "
                  "[[anchor]], [text], a|b, a<b & c>d, a + b +, back\\slash, 'quoted' -- dashed... see http://example.org/x_y."},
    {"kind": "recommendation", "id": "/rec/core/stable-ids", "statement": "A document SHOULD keep ids stable."},
    {"kind": "permission", "id": "/per/core/extra-fields", "statement": "A document MAY carry extra fields."},
    {"kind": "abstract_test", "id": "/conf/core/valid-document", "target": "/req/core/valid-document",
     "purpose": "Verify validity.", "steps": ["Validate the document against the schema."]},
    {"kind": "abstract_test", "id": "/conf/core/stable-ids-listed", "target": "/req/core/stable-ids-listed",
     "purpose": "Verify listing."},
    {"kind": "abstract_test", "id": "/conf/core/special-chars", "target": "/req/core/special-chars",
     "purpose": "Verify *escaping* of {name}.", "steps": ["Check key:: value, then a|b."]},
    {"kind": "conformance_class", "id": "/conf/core", "target": "/req/core",
     "tests": ["/conf/core/valid-document", "/conf/core/stable-ids-listed", "/conf/core/special-chars"]},
]
CONFIG = f'''records_dir = "records"
[[normative_references]]
name = "Example dependency"
uri_prefix = "http://www.opengis.net/spec/example-dep/1.0/"
'''
HEADER = """= Example Round Trip Standard
:doctype: standard
:encoding: utf-8
:lang: en
:status: swg-draft
:committee: technical
:external-id: http://www.opengis.net/doc/IS/roundtrip/1.0
:docnumber: 99-998
:received-date: 2026-11-06
:issued-date: 2026-11-06
:published-date: 2026-11-06
:fullname: Round Trip Author
:docsubtype: implementation
:keywords: ogcdoc, OGC document, roundtrip
:submitting-organizations: Example Org
:mn-document-class: ogc
:mn-output-extensions: xml
:local-cache-only:
:data-uri-image:
:edition: 1.0.0

[abstract]
== Abstract
Round trip document.

== Preface
Preface.

== Scope
Scope.

== Conformance
This standard defines one conformance class.

include::conformance-classes.adoc[]

[bibliography]
== Normative references
* [[[dep,OGC 99-000]]], Example dependency

== Terms and definitions
No terms.

== Core requirements class

include::requirements.adoc[]

[appendix,obligation=normative]
== Abstract test suite

include::abstract-tests.adoc[]
"""


class EmitUnitTests(unittest.TestCase):
    def test_output_is_deterministic_and_independent_of_input_order(self):
        a = emit.emit(RECORDS)
        b = emit.emit(list(reversed(RECORDS)))
        self.assertEqual(a, b)

    def test_whitespace_in_statements_is_collapsed(self):
        text = emit.emit(RECORDS)["requirements.adoc"]
        self.assertIn("part:: pass:c[A document SHALL list its identifiers.]", text)

    def test_one_inherit_and_requirement_line_per_entry(self):
        text = emit.emit(RECORDS)["requirements.adoc"]
        self.assertEqual(text.count("inherit:: "), 2)
        self.assertEqual(text.count("requirement:: "), 3)

    def test_steps_become_a_test_method_and_absent_steps_do_not(self):
        text = emit.emit(RECORDS)["abstract-tests.adoc"]
        self.assertEqual(text.count("test-method::"), 2)

    def test_unknown_kind_is_refused(self):
        with self.assertRaises(ValueError):
            emit.emit([{"kind": "mystery", "id": "/x"}])

    def test_backslash_before_closing_bracket_is_refused(self):
        with self.assertRaises(ValueError):
            emit.emit([{"kind": "permission", "id": "/per/a/b", "statement": "A MAY use a\\] b."}])

    def test_markup_is_emitted_as_literal_text(self):
        text = emit.emit(RECORDS)["requirements.adoc"]
        self.assertIn("part:: pass:c[A key:: value SHALL be {name} escaped, *bold*", text)

    def test_record_without_id_is_refused(self):
        with self.assertRaises(ValueError):
            emit.emit([{"kind": "requirement"}])


def image_available():
    return bool(IMAGE) and wrapper.image_present(IMAGE)


@unittest.skipUnless(image_available(), "SKIPPED: pinned Metanorma image not present locally; round trip not run")
class RoundTrip(unittest.TestCase):
    def test_emitted_records_compile_and_come_back_identical(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "records" / "all.yaml").write_text(yaml.safe_dump(RECORDS), encoding="utf-8")
            (root / "ogcspec.gate.toml").write_text(CONFIG, encoding="utf-8")
            emit.main(["--records", str(root / "records"), "--out", str(root / "build")])
            (root / "build" / "doc.adoc").write_text(HEADER, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(HERE.parent / "metanorma.py"), "--image", IMAGE,
                                   "--adoc", str(root / "build" / "doc.adoc"), "--formats", "xml"],
                                  capture_output=True, text=True)
            (root / "build" / "compile.json").write_text(proc.stdout or "{}", encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
            code, summary = gate.run(root / "ogcspec.gate.toml", None, root / "build" / "doc.xml",
                                     root / "build" / "compile.json", root / "build" / "doc.err.html")
            fidelity = [f for f in summary["findings"] if f["rule"] in ("X000", "X001", "X002", "X003")]
            self.assertEqual(fidelity, [])
            rules = [f for f in summary["findings"] if f["rule"][0] in "GMPS"]
            self.assertEqual(rules, [])
            print("\nround trip messages:", sorted({f["key"] for f in summary["findings"] if f["rule"] == "X010"}),
                  file=sys.stderr)


# --- plan step 3: titles, derived conformance-class dependencies, profile, record-only fields.
# A separate fixture: RECORDS, CONFIG and HEADER above are imported by docs/design/*.py and must not change.
DEP_EXT = "https://example.org/spec/dep/1.0/conf/base"
STEP3_RECORDS = [
    {"kind": "requirements_class", "id": "/req/core", "title": "Core *bold* -- 'q' {name}", "status": "proposed",
     "uml_package": "example::core", "subject": "Example document", "requirements": ["/req/core/first"]},
    {"kind": "requirement", "id": "/req/core/first", "status": "proposed", "statement": "A document SHALL do the first thing."},
    {"kind": "abstract_test", "id": "/conf/core/first", "target": "/req/core/first", "purpose": "Verify the first thing."},
    {"kind": "conformance_class", "id": "/conf/core", "title": "Core conformance", "status": "proposed",
     "target": "/req/core", "tests": ["/conf/core/first"]},
    {"kind": "requirements_class", "id": "/req/ext", "title": "Extension", "uml_package": "example::ext",
     "subject": "Example document", "inherit": ["/req/core"], "requirements": ["/req/ext/second"]},
    {"kind": "requirement", "id": "/req/ext/second", "statement": "A document SHALL do the second thing."},
    {"kind": "abstract_test", "id": "/conf/ext/second", "target": "/req/ext/second", "purpose": "Verify the second thing."},
    {"kind": "conformance_class", "id": "/conf/ext", "target": "/req/ext", "depends_on": [DEP_EXT],
     "tests": ["/conf/ext/second"]},
    {"kind": "requirements_class", "id": "/req/prof", "title": "Profile", "uml_package": "example::prof", "profile": True,
     "subject": "Example document", "inherit": ["/req/core", "/req/ext"], "requirements": []},
    {"kind": "conformance_class", "id": "/conf/prof", "target": "/req/prof", "tests": []},
]
# top-level keys must come before the first [[normative_references]] table or TOML puts them inside it
STEP3_CONFIG = 'core = "/req/core"\nstyle = ["uml"]\n' + CONFIG + \
    '[[normative_references]]\nname = "Example base"\nuri_prefix = "https://example.org/spec/dep/1.0/"\n'


class Step3EmitUnitTests(unittest.TestCase):
    def emitted(self, records=STEP3_RECORDS, namespace=""):
        return emit.emit(copy_records(records), namespace)

    def test_title_is_a_literal_block_title_between_style_and_delimiter(self):
        text = self.emitted()["requirements.adoc"]
        self.assertIn("[requirements_class]\n.pass:c[Core *bold* -- 'q' {name}]\n====\n[%metadata]\nidentifier:: /req/core\n", text)

    def test_no_title_no_block_title_line(self):
        records = [dict(r) for r in STEP3_RECORDS]
        for r in records:
            r.pop("title", None)
        self.assertNotIn("\n.", self.emitted(records)["requirements.adoc"])

    def test_conformance_classes_carry_derived_then_authored_dependencies(self):
        text = self.emitted()["conformance-classes.adoc"]
        self.assertIn("identifier:: /conf/ext\ninherit:: /conf/core\ninherit:: " + DEP_EXT + "\ntarget:: /req/ext\n", text)
        self.assertIn("identifier:: /conf/prof\ninherit:: /conf/core\ninherit:: /conf/ext\ntarget:: /req/prof\n", text)
        core = text.split("identifier:: /conf/core\n", 1)[1].split("====", 1)[0]
        self.assertNotIn("inherit::", core)

    def test_record_only_fields_are_not_emitted(self):
        joined = "\n".join(self.emitted().values())
        for word in ("status", "uml_package", "example::", "profile", "depends_on", "proposed"):
            self.assertNotIn(word, joined)

    def test_a_profile_is_two_ordinary_blocks_with_no_requirements_or_tests(self):
        out = self.emitted()
        prof = out["requirements.adoc"].split("identifier:: /req/prof\n", 1)[1].split("====", 1)[0]
        self.assertNotIn("requirement::", prof)
        conf = out["conformance-classes.adoc"].split("identifier:: /conf/prof\n", 1)[1].split("====", 1)[0]
        self.assertNotIn("conformance-test::", conf)

    def test_a_backslash_before_a_closing_bracket_in_a_title_is_refused(self):
        records = [dict(r) for r in STEP3_RECORDS]
        records[0]["title"] = "bad\\] title"
        with self.assertRaises(ValueError):
            emit.emit(records)

    def test_emitter_and_gate_derive_the_same_dependencies(self):
        ns = "https://www.opengis.net/spec/x-1/1.0"
        absolute = [dict(r) for r in STEP3_RECORDS]
        for r in absolute:
            r["id"] = ns + r["id"]
            for field in ("target", "inherit", "requirements", "tests"):
                if field in r:
                    r[field] = [ns + v for v in r[field]] if isinstance(r[field], list) else ns + r[field]
        absolute[8]["inherit"] = [ns + "/req/core", "Extension"]  # one entry by identifier, one by title
        ambiguous = [dict(r) for r in STEP3_RECORDS] + [
            {"kind": "conformance_class", "id": "/conf/core-again", "target": "/req/core", "tests": []}]
        duplicated = [dict(r) for r in STEP3_RECORDS]
        duplicated[7] = dict(duplicated[7], depends_on=[DEP_EXT, DEP_EXT, "/conf/ext"])
        for name, records, namespace in (("plain", STEP3_RECORDS, ""), ("namespace and title", absolute, ns),
                                         ("ambiguous", ambiguous, ""), ("duplicates", duplicated, ""),
                                         ("namespace not configured", absolute, "")):
            self.assertEqual(emit.conformance_inherit(records, namespace),
                             gate.conformance_inherit(records, {"namespace": namespace} if namespace else {}), name)

    def test_config_supplies_the_namespace_on_the_command_line(self):
        ns = "https://www.opengis.net/spec/x-1/1.0"
        records = [
            {"kind": "requirements_class", "id": f"{ns}/req/core", "subject": "S", "requirements": []},
            {"kind": "conformance_class", "id": f"{ns}/conf/core", "target": "/req/core", "tests": []},
            {"kind": "requirements_class", "id": "/req/a", "subject": "S", "inherit": [f"{ns}/req/core"], "requirements": []},
            {"kind": "conformance_class", "id": "/conf/a", "target": "/req/a", "tests": []},
        ]
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "records" / "all.yaml").write_text(yaml.safe_dump(records), encoding="utf-8")
            (root / "cfg.toml").write_text(f'namespace = "{ns}"\n', encoding="utf-8")
            self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "o"), "--config", str(root / "cfg.toml")]), 0)
            text = (root / "o" / "conformance-classes.adoc").read_text(encoding="utf-8")
            self.assertIn(f"identifier:: /conf/a\ninherit:: {ns}/conf/core\n", text)
            self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "o2")]), 0)
            self.assertNotIn("inherit::", (root / "o2" / "conformance-classes.adoc").read_text(encoding="utf-8"))
            self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "o3"), "--config", str(root / "missing.toml")]), 2)


def copy_records(records):
    return [dict(r) for r in records]


@unittest.skipUnless(image_available(), "SKIPPED: pinned Metanorma image not present locally; round trip not run")
class Step3RoundTrip(unittest.TestCase):
    def test_titles_derived_dependencies_and_a_profile_survive_compile_and_gate(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "records" / "all.yaml").write_text(yaml.safe_dump(STEP3_RECORDS), encoding="utf-8")
            (root / "ogcspec.gate.toml").write_text(STEP3_CONFIG, encoding="utf-8")
            self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "build"),
                                        "--config", str(root / "ogcspec.gate.toml")]), 0)
            (root / "build" / "doc.adoc").write_text(HEADER, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(HERE.parent / "metanorma.py"), "--image", IMAGE,
                                   "--adoc", str(root / "build" / "doc.adoc"), "--formats", "xml"],
                                  capture_output=True, text=True)
            (root / "build" / "compile.json").write_text(proc.stdout or "{}", encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
            code, summary = gate.run(root / "ogcspec.gate.toml", None, root / "build" / "doc.xml",
                                     root / "build" / "compile.json", root / "build" / "doc.err.html")
            fidelity = [f for f in summary["findings"] if f["rule"] in ("X000", "X001", "X002", "X003")]
            self.assertEqual(fidelity, [])
            rules = [f for f in summary["findings"] if f["rule"][0] in "GMPS"]
            self.assertEqual(rules, [])
            messages = {f["key"] for f in summary["findings"] if f["rule"] == "X010"}
            # Metanorma's own linkage check warns about the empty profile classes: accepted only through a baseline
            self.assertIn("MODSPEC_1:/req/prof", messages)
            self.assertIn("MODSPEC_1:/conf/prof", messages)
            self.assertFalse([m for m in messages if m.startswith(("STANDOC_7", "STANDOC_38"))], messages)


class TermEmitUnitTests(unittest.TestCase):
    TERM = {"kind": "term", "id": "/term/sensor", "term": "Sensor (physical)", "aliases": ["detector"],
            "definition": "A device & its _probe_.", "note": "Out of scope: software.", "source": "dep", "modified": True,
            "mappings": [{"relation": "close", "ontology": "o", "iri": "https://example.org/onto#Sensor", "note": "record-only"}]}

    def test_a_term_becomes_one_literal_entry_in_terms_adoc(self):
        text = emit.emit([self.TERM])["terms.adoc"]
        self.assertEqual(text, "\n".join([
            "=== pass:c[Sensor (physical)]", "alt:[pass:c[detector]]", "", "pass:c[A device & its _probe_.]", "",
            "NOTE: Mapping (close): https://example.org/onto#Sensor", "", "NOTE: pass:c[Out of scope: software.]", "",
            "[.source]", "<<dep>>, modified"]) + "\n")

    def test_the_per_mapping_note_is_record_only(self):
        self.assertNotIn("record-only", emit.emit([self.TERM])["terms.adoc"])

    def test_terms_adoc_is_written_only_when_there_are_terms(self):
        self.assertNotIn("terms.adoc", emit.emit(RECORDS))
        self.assertIn("terms.adoc", emit.emit(RECORDS + [self.TERM]))

    def test_other_files_are_unchanged_by_terms(self):
        self.assertEqual({k: v for k, v in emit.emit(RECORDS + [self.TERM]).items() if k != "terms.adoc"}, emit.emit(RECORDS))

    def test_terms_are_ordered_by_identifier_and_independent_of_input_order(self):
        a = dict(self.TERM, id="/term/a", term="A")
        b = dict(self.TERM, id="/term/b", term="B")
        self.assertEqual(emit.emit([b, a])["terms.adoc"], emit.emit([a, b])["terms.adoc"])

    def test_unsafe_text_is_refused(self):
        for field, value in (("term", "Bad]"), ("definition", "x\\"), ("note", "n]"), ("aliases", ["ok", "a]"])):
            with self.assertRaises(ValueError, msg=field):
                emit.emit([dict(self.TERM, **{field: value})])
        for iri in ("https://x/a b", "https://x/<a>", "https://x/[a]", ""):
            with self.assertRaises(ValueError, msg=iri):
                emit.emit([dict(self.TERM, mappings=[{"relation": "close", "ontology": "o", "iri": iri}])])
        with self.assertRaises(ValueError):
            emit.emit([dict(self.TERM, note="Mapping (close): https://example.org/x")])

    def test_a_term_without_source_or_aliases_has_neither(self):
        text = emit.emit([{"kind": "term", "id": "/term/p", "term": "Plain", "definition": "d"}])["terms.adoc"]
        self.assertEqual(text, "=== pass:c[Plain]\n\npass:c[d]\n")


TERM_RECORDS = [
    {"kind": "term", "id": "/term/sensor", "term": "Sensor (physical)", "aliases": ["detector", "sensing *device* & co"],
     "definition": "A device & its _probe_ that responds to a property of the world.",
     "mappings": [{"relation": "close", "ontology": "example-onto", "iri": "https://example.org/onto#Sensor", "note": "record-only"},
                  {"relation": "broader", "ontology": "example-onto", "iri": "https://example.org/onto#System"}],
     "note": "Software sensors are out of scope.", "source": "dep", "modified": True},
    {"kind": "term", "id": "/term/observation", "term": "Observation", "definition": "The act of estimating a value.",
     "source": "dep"},
    {"kind": "term", "id": "/term/plain", "term": "Plain term", "definition": "Nothing extra."},
]
TERM_CONFIG = '''records_dir = "records"

[[ontologies]]
key = "example-onto"
iri_prefix = "https://example.org/onto#"
'''
# a hand-written term the records do not own: the gate must not report it
HAND_WRITTEN_TERM = "=== hand written\n\npass:c[A term the records do not define.]\n"


def terms_document(terms_adoc):
    return HEADER.replace("== Terms and definitions\nNo terms.\n",
                          "[heading=terms and definitions]\n== Terms and definitions\n\ninclude::terms.adoc[]\n\n" + HAND_WRITTEN_TERM)


@unittest.skipUnless(image_available(), "SKIPPED: pinned Metanorma image not present locally; round trip not run")
class TermsRoundTrip(unittest.TestCase):
    def build(self, records):
        """Emit, compile on the pinned image; returns the temporary project root (kept until the test ends)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "records").mkdir()
        (root / "records" / "all.yaml").write_text(yaml.safe_dump(RECORDS + records), encoding="utf-8")
        (root / "ogcspec.gate.toml").write_text(TERM_CONFIG, encoding="utf-8")
        self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "build"),
                                    "--config", str(root / "ogcspec.gate.toml")]), 0)
        (root / "build" / "doc.adoc").write_text(terms_document(None), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(HERE.parent / "metanorma.py"), "--image", IMAGE,
                               "--adoc", str(root / "build" / "doc.adoc"), "--formats", "xml"],
                              capture_output=True, text=True)
        (root / "build" / "compile.json").write_text(proc.stdout or "{}", encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        return root

    def gate_findings(self, root):
        _, summary = gate.run(root / "ogcspec.gate.toml", None, root / "build" / "doc.xml",
                              root / "build" / "compile.json", root / "build" / "doc.err.html")
        return summary

    def test_terms_compile_and_come_back_identical(self):
        root = self.build(TERM_RECORDS)
        summary = self.gate_findings(root)
        fidelity = [(f["rule"], f["key"]) for f in summary["findings"] if f["rule"] in ("X000", "X001", "X002", "X003")]
        self.assertEqual(fidelity, [])  # includes: the hand-written term in the same clause is not an X002
        self.assertEqual([f for f in summary["findings"] if f["rule"][0] in "GMPST"], [])
        messages = {f["key"] for f in summary["findings"] if f["rule"] == "X010"}
        self.assertFalse([m for m in messages if m.startswith(("STANDOC_7", "STANDOC_20", "STANDOC_25"))], messages)
        xml_terms = {t["term"]: t for t in gate.terms_from_xml(root / "build" / "doc.xml")}
        self.assertEqual(sorted(xml_terms), ["Observation", "Plain term", "Sensor (physical)", "hand written"])
        sensor = xml_terms["Sensor (physical)"]
        self.assertEqual(sensor["aliases"], ["detector", "sensing *device* & co"])
        self.assertEqual([(m["relation"], m["iri"]) for m in sensor["mappings"]],
                         [("close", "https://example.org/onto#Sensor"), ("broader", "https://example.org/onto#System")])
        self.assertEqual((sensor["source"], sensor["modified"], sensor["note"]), ("dep", True, "Software sensors are out of scope."))
        self.assertEqual((xml_terms["Observation"]["source"], xml_terms["Observation"]["modified"]), ("dep", False))

    def test_a_changed_record_and_a_missing_term_are_reported(self):
        root = self.build(TERM_RECORDS)
        changed = yaml.safe_load((root / "records" / "all.yaml").read_text(encoding="utf-8"))
        for r in changed:
            if r.get("id") == "/term/sensor":
                r["definition"] = "Changed after the document was built."
                r["mappings"][0]["iri"] = "https://example.org/onto#Other"
                r["source"] = "other"
        changed.append({"kind": "term", "id": "/term/ghost", "term": "Ghost", "definition": "Not in the document."})
        (root / "records" / "all.yaml").write_text(yaml.safe_dump(changed), encoding="utf-8")
        found = {(f["rule"], f["key"]) for f in self.gate_findings(root)["findings"]}
        self.assertIn(("X001", "term:/term/ghost"), found)
        for field in ("definition", "mappings", "source"):
            self.assertIn(("X003", f"/term/sensor#{field}"), found)
        self.assertNotIn(("X003", "/term/observation#definition"), found)
        self.assertFalse([k for r, k in found if r == "X002" and "term" in k])


@unittest.skipUnless(image_available(), "SKIPPED: pinned Metanorma image not present locally; round trip not run")
class WorkedExampleBaseline(unittest.TestCase):
    """The worked example in ogcspec-modspec/references passes the gate, stage 2 included, with exactly its baseline file.
    The baseline holds the example's two empty-profile messages and external-dependency messages, plus two that come from
    the test document's header and offline bibliography (OGC_14, STANDOC_40)."""

    def test_example_and_its_baseline_exit_zero(self):
        refs = SKILLS / "ogcspec-modspec" / "references"
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            shutil.copy(refs / "record-format-example.yaml", root / "records" / "all.yaml")
            (root / "ogcspec.gate.toml").write_text(
                'records_dir = "records"\ncore = "/req/core"\nstyle = ["uml"]\n[[normative_references]]\n'
                'name = "Example dependency"\nuri_prefix = "https://example.org/spec/dep/1.0/"\n', encoding="utf-8")
            self.assertEqual(emit.main(["--records", str(root / "records"), "--out", str(root / "build"),
                                        "--config", str(root / "ogcspec.gate.toml")]), 0)
            (root / "build" / "doc.adoc").write_text(
                HEADER.replace("http://www.opengis.net/spec/example-dep/1.0/", "https://example.org/spec/dep/1.0/"),
                encoding="utf-8")
            proc = subprocess.run([sys.executable, str(HERE.parent / "metanorma.py"), "--image", IMAGE,
                                   "--adoc", str(root / "build" / "doc.adoc"), "--formats", "xml"],
                                  capture_output=True, text=True)
            (root / "build" / "compile.json").write_text(proc.stdout or "{}", encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
            args = (root / "ogcspec.gate.toml", refs / "record-format-example.baseline.json", root / "build" / "doc.xml",
                    root / "build" / "compile.json", root / "build" / "doc.err.html")
            code, summary = gate.run(*args)
            self.assertEqual(summary["baseline"], {"unexpected": [], "missing": []})
            self.assertEqual(code, 0)
            # and the baseline is load-bearing: without it the same run fails
            code, _ = gate.run(args[0], None, *args[2:])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
