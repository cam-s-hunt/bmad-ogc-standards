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


if __name__ == "__main__":
    unittest.main()
