"""Stage 2 tests. Fixtures are real Metanorma output (image digest in METANORMA-PIN), copied from the
2026-11-06 spike; see docs/metanorma-spike-2026-11-06.md."""
import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "gate.py"
spec = importlib.util.spec_from_file_location("gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate"] = gate
spec.loader.exec_module(gate)

FIX = Path(__file__).resolve().parent / "fixtures"
DEP = "http://www.opengis.net/spec/example-dep/1.0/conf/core"
CONFIG = f'''records_dir = "records"
verbal_form = "SHALL"

[[normative_references]]
name = "Example dependency"
uri_prefix = "http://www.opengis.net/spec/example-dep/1.0/"
'''
# The YAML equivalent of spike/gen_spike.py's clean document.
SPIKE = [
    {"kind": "requirements_class", "id": "/req/core", "subject": "Example document",
     "inherit": [DEP], "requirements": ["/req/core/valid-document"]},
    {"kind": "requirement", "id": "/req/core/valid-document", "statement": "A document SHALL validate against the schema."},
    {"kind": "recommendation", "id": "/rec/core/stable-ids", "statement": "A document SHOULD keep ids stable."},
    {"kind": "permission", "id": "/per/core/extra-fields", "statement": "A document MAY carry extra fields."},
    {"kind": "abstract_test", "id": "/conf/core/valid-document", "target": "/req/core/valid-document",
     "purpose": "Verify validity.", "steps": ["Validate the document against the schema."]},
    {"kind": "conformance_class", "id": "/conf/core", "target": "/req/core", "tests": ["/conf/core/valid-document"]},
]


def stage2(case, records=SPIKE, baseline=None):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "records").mkdir()
    (root / "g.toml").write_text(CONFIG, encoding="utf-8")
    (root / "records" / "all.yaml").write_text(yaml.safe_dump(records), encoding="utf-8")
    d = FIX / case
    xml = d / "doc.xml"
    with tmp:
        code, summary = gate.run(root / "g.toml", baseline, xml, d / "compile.json", d / "doc.err.html")
    return code, summary


def idents(summary):
    return sorted({f"{f['rule']}:{f['key']}" for f in summary["findings"]})


class ExtractorTests(unittest.TestCase):
    def test_clean_document_yields_the_six_definitions_not_the_list_entries(self):
        records = gate.records_from_xml(FIX / "c1_clean" / "doc.xml")
        self.assertEqual(sorted((r["kind"], r["id"]) for r in records), sorted((r["kind"], r["id"]) for r in SPIKE))

    def test_fields_are_rebuilt(self):
        by_id = {r["id"]: r for r in gate.records_from_xml(FIX / "c1_clean" / "doc.xml")}
        self.assertEqual(by_id["/req/core"]["requirements"], ["/req/core/valid-document"])
        self.assertEqual(by_id["/req/core"]["inherit"], [DEP])
        self.assertEqual(by_id["/req/core"]["subject"], "Example document")
        self.assertEqual(by_id["/conf/core"]["tests"], ["/conf/core/valid-document"])
        self.assertEqual(by_id["/conf/core/valid-document"]["target"], "/req/core/valid-document")
        self.assertEqual(by_id["/req/core/valid-document"]["statement"], "A document SHALL validate against the schema.")

    def test_messages_are_parsed_with_ids_and_severity(self):
        msgs = gate.messages_from_html(FIX / "c1_clean" / "doc.err.html")
        self.assertIn("MODSPEC_2", {m["id"] for m in msgs})
        self.assertTrue(all(isinstance(m["severity"], int) for m in msgs))

    def test_message_keys_ignore_object_ids(self):
        a = {"id": "STANDOC_16", "ident": "--", "message": "Section #<Asciidoctor::Section@10648 {x}>"}
        b = {"id": "STANDOC_16", "ident": "--", "message": "Section #<Asciidoctor::Section@99 {x}>"}
        self.assertEqual(gate.message_key(a), gate.message_key(b))


class CanonTests(unittest.TestCase):
    def test_typography_is_normalised_and_nothing_else(self):
        self.assertEqual(gate.canon("a \u2018b\u2019 \u201cc\u201d \u2014 d\u2026"), "a 'b' \"c\" -- d...")
        self.assertNotEqual(gate.canon("a SHALL b"), gate.canon("a SHOULD b"))
        self.assertNotEqual(gate.canon("a <<x>> b"), gate.canon("a b"))

    def test_empty_link_renders_its_target(self):
        import xml.etree.ElementTree as ET
        e = ET.fromstring('<p xmlns="x">see <link target="http://e.org/a_b"/> now</p>')
        self.assertEqual(gate._text(e), "see http://e.org/a_b now")


SHAPES = """<metanorma xmlns="https://www.metanorma.org/ns/standoc">
<annex obligation="normative" id="a1">
<requirement model="ogc" type="class" anchor="rc_core"><identifier>/req/core</identifier><title>Core</title>
 <subject>Web API</subject><requirement type="general"><identifier>/req/core/free</identifier></requirement></requirement>
<requirement model="ogc" type="class" anchor="rc_ext"><identifier>/req/ext</identifier>
 <inherit><xref target="rc_core"><display-text>Core</display-text></xref></inherit>
 <classification><tag>Target Type</tag><value>Web API</value></classification></requirement>
<requirement model="ogc" type="conformanceclass" anchor="cc_core"><identifier>/conf/core</identifier>
 <subject><xref target="rc_core"/></subject><requirement type="verification"><identifier>/conf/core/free</identifier></requirement></requirement>
<requirement model="ogc" type="conformanceclass" anchor="cc_short"><description><dl><dt>target</dt></dl></description></requirement>
<requirement model="ogc" anchor="r_free"><identifier>/req/core/free</identifier>
 <description><p>A server <em>SHALL</em> do it.</p></description></requirement>
<requirement model="ogc" anchor="r_parts"><identifier>/req/core/parts</identifier>
 <component class="conditions"><p>If x,</p></component><component class="part"><p>y SHALL hold.</p></component></requirement>
<requirement model="ogc" type="abstracttest" anchor="t1"><identifier>/conf/core/free</identifier>
 <classification><tag>target</tag><value>/req/core/free</value></classification></requirement>
<requirement model="ogc" anchor="r_noid"><component class="part"><p>No identifier SHALL be here.</p></component></requirement>
</annex></metanorma>"""


class ShapeTests(unittest.TestCase):
    """Markup shapes found in real documents (ModSpec, Processes, Records, Connected Systems)."""

    def scan(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "d.xml"
            p.write_text(SHAPES, encoding="utf-8")
            records, notes = gate.scan_xml(p)
            return {(r["id"] or r["_anchor"]): r for r in records}, notes, gate.annex_findings(p)

    def test_free_body_text_is_the_statement_and_conditions_are_not(self):
        by_id, _, _ = self.scan()
        self.assertEqual(by_id["/req/core/free"]["statement"], "A server SHALL do it.")
        self.assertEqual(by_id["/req/core/parts"]["statement"], "y SHALL hold.")

    def test_target_type_from_subject_or_classification(self):
        by_id, _, _ = self.scan()
        self.assertEqual(by_id["/req/core"]["subject"], "Web API")
        self.assertEqual(by_id["/req/ext"]["subject"], "Web API")
        self.assertEqual(by_id["/req/core"]["title"], "Core")

    def test_inherit_written_as_an_xref_resolves_to_the_class_identifier(self):
        by_id, _, _ = self.scan()
        self.assertEqual(by_id["/req/ext"]["inherit"], ["/req/core"])

    def test_conformance_class_target_resolves_through_an_xref_to_the_class_anchor(self):
        by_id, _, _ = self.scan()
        self.assertEqual(by_id["/conf/core"]["target"], "/req/core")
        self.assertEqual(by_id["/conf/core"]["tests"], ["/conf/core/free"])

    def test_shorthand_classes_are_counted_not_turned_into_records(self):
        by_id, notes, _ = self.scan()
        self.assertEqual(notes["shorthand_without_identifier"], 1)
        self.assertNotIn("cc_short", by_id)

    def test_a_provision_without_an_identifier_is_a_record_and_m001_reports_it(self):
        by_id, _, _ = self.scan()
        self.assertIn("r_noid", by_id)
        found, _ = gate.check(list(by_id.values()), {})
        self.assertIn(("M001", "r_noid"), {(f.rule, f.key) for f in found})

    def test_annex_designation_is_read(self):
        _, _, annex = self.scan()
        self.assertEqual(annex, [])

    def test_abstract_test_in_an_informative_annex_is_p001(self):
        findings = gate.annex_findings(FIX / "c1_clean" / "doc.xml")
        self.assertEqual([f.rule for f in findings], ["P001"])

    def test_zero_definitions_in_a_compiled_document_is_a_finding_not_a_clean_pass(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "g.toml").write_text('records_dir = "records"\n', encoding="utf-8")
            (root / "d.xml").write_text('<metanorma xmlns="https://www.metanorma.org/ns/standoc"><sections/></metanorma>',
                                        encoding="utf-8")
            code, summary = gate.run(root / "g.toml", None, root / "d.xml")
        self.assertEqual(code, 1)
        self.assertIn("X004:d.xml", idents(summary))


class Stage2Tests(unittest.TestCase):
    def test_clean_document_has_only_metanorma_messages(self):
        code, summary = stage2("c1_clean")
        rules = {f["rule"] for f in summary["findings"]}
        # P001: the spike fixtures put the test suite in an annex that is not designated normative
        self.assertEqual(rules, {"X010", "P001"}, idents(summary))
        self.assertEqual(code, 1)  # messages need a baseline to be accepted

    def test_clean_document_passes_with_its_messages_baselined(self):
        _, summary = stage2("c1_clean")
        with tempfile.TemporaryDirectory() as t:
            base = Path(t) / "b.json"
            base.write_text('{"expected": %s}' % __import__("json").dumps(idents(summary)), encoding="utf-8")
            code, summary = stage2("c1_clean", baseline=base)
        self.assertEqual(code, 0, summary.get("baseline"))

    def test_untested_requirement_is_a_gate_finding_even_though_metanorma_exits_zero(self):
        recs = [r for r in copy.deepcopy(SPIKE) if r["kind"] != "abstract_test"]
        recs[-1]["tests"] = []
        _, summary = stage2("c2_untested_req", recs)
        found = idents(summary)
        self.assertIn("M007:xml:/req/core/valid-document", found)

    def test_compile_abort_fails_closed(self):
        code, summary = stage2("c3_dup_id")
        found = idents(summary)
        self.assertEqual(code, 1)
        self.assertIn("X000:doc.xml", found)
        self.assertTrue(any(f.startswith("X010:") and ("STANDOC_36" in f or "MODSPEC_3" in f) for f in found), found)

    def test_dangling_internal_inherit_is_found_by_the_xml_rules(self):
        recs = copy.deepcopy(SPIKE)
        recs[0]["inherit"] = ["/req/nowhere"]
        _, summary = stage2("c4_bad_inherit", recs)
        self.assertIn("M009:xml:/req/core>/req/nowhere", idents(summary))

    def test_fidelity_detects_a_record_missing_from_the_xml(self):
        recs = copy.deepcopy(SPIKE) + [{"kind": "permission", "id": "/per/core/extra", "statement": "A MAY B."}]
        _, summary = stage2("c1_clean", recs)
        self.assertIn("X001:permission:/per/core/extra", idents(summary))

    def test_fidelity_detects_changed_text(self):
        recs = copy.deepcopy(SPIKE)
        recs[1]["statement"] = "A document SHALL do something else."
        _, summary = stage2("c1_clean", recs)
        self.assertIn("X003:/req/core/valid-document#statement", idents(summary))

    def test_fidelity_detects_an_xml_only_record(self):
        recs = [r for r in copy.deepcopy(SPIKE) if r["id"] != "/per/core/extra-fields"]
        _, summary = stage2("c1_clean", recs)
        self.assertIn("X002:permission:/per/core/extra-fields", idents(summary))

    def test_missing_xml_without_abort_file_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "g.toml").write_text(CONFIG, encoding="utf-8")
            code, summary = gate.run(root / "g.toml", None, root / "doc.xml")
        self.assertEqual(code, 1)
        self.assertIn("X000:doc.xml", idents(summary))

    def _with_compile_result(self, content):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "records" / "all.yaml").write_text(yaml.safe_dump(SPIKE), encoding="utf-8")
            (root / "g.toml").write_text(CONFIG, encoding="utf-8")
            (root / "c.json").write_text(content, encoding="utf-8")
            return gate.run(root / "g.toml", None, FIX / "c1_clean" / "doc.xml", root / "c.json",
                            FIX / "c1_clean" / "doc.err.html")

    def test_compile_result_must_say_exit_zero_explicitly(self):
        for content in ("", "{}", "not json", "[]", '{"exit": null}', '{"exit": true}', '{"exit": "0"}', '{"exit": 3}'):
            with self.subTest(content=content):
                code, summary = self._with_compile_result(content)
                self.assertEqual(code, 1)
                self.assertIn("X000:doc.xml", idents(summary))

    def test_explicit_exit_zero_is_accepted(self):
        _, summary = self._with_compile_result('{"exit": 0}')
        self.assertNotIn("X000:doc.xml", idents(summary))

    def test_changed_purpose_and_steps_are_detected(self):
        recs = copy.deepcopy(SPIKE)
        recs[4]["purpose"] = "Something else."
        recs[4]["steps"] = ["Do another thing."]
        found = idents(stage2("c1_clean", recs)[1])
        self.assertIn("X003:/conf/core/valid-document#purpose", found)
        self.assertIn("X003:/conf/core/valid-document#steps", found)

    def test_nonzero_compile_exit_fails_even_with_xml_present(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "records").mkdir()
            (root / "records" / "all.yaml").write_text(yaml.safe_dump(SPIKE), encoding="utf-8")
            (root / "g.toml").write_text(CONFIG, encoding="utf-8")
            (root / "c.json").write_text('{"exit": 7}', encoding="utf-8")
            code, summary = gate.run(root / "g.toml", None, FIX / "c1_clean" / "doc.xml", root / "c.json")
        self.assertIn("X000:doc.xml", idents(summary))


if __name__ == "__main__":
    unittest.main()
