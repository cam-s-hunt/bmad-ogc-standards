import copy
import importlib.util
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "gate.py"
spec = importlib.util.spec_from_file_location("gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate"] = gate  # dataclasses resolves annotations through sys.modules
spec.loader.exec_module(gate)

DEP = "http://www.opengis.net/spec/example-dep/1.0/conf/core"
GOOD = [
    {"kind": "requirements_class", "id": "/req/core", "subject": "Capability specification document",
     "inherit": [DEP], "requirements": ["/req/core/valid-document"]},
    {"kind": "requirement", "id": "/req/core/valid-document", "statement": "A document SHALL validate against the schema."},
    {"kind": "recommendation", "id": "/rec/core/stable-ids", "statement": "A document SHOULD keep ids stable."},
    {"kind": "abstract_test", "id": "/conf/core/valid-document", "target": "/req/core/valid-document", "purpose": "Verify validity."},
    {"kind": "conformance_class", "id": "/conf/core", "target": "/req/core", "tests": ["/conf/core/valid-document"]},
]
CONFIG = '''records_dir = "records"
core = "/req/core"

[[normative_references]]
name = "Example dependency"
uri_prefix = "http://www.opengis.net/spec/example-dep/1.0/"
'''


def build(records, config=CONFIG):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "records").mkdir()
    (root / "ogcspec.gate.toml").write_text(config, encoding="utf-8")
    (root / "records" / "all.yaml").write_text(yaml.safe_dump(records), encoding="utf-8")
    return tmp, root / "ogcspec.gate.toml"


def rules(records, config=CONFIG):
    tmp, cfg = build(records, config)
    with tmp:
        code, summary = gate.run(cfg, None)
    return code, sorted({f["rule"] for f in summary["findings"]}), summary


def mutate(fn):
    records = copy.deepcopy(GOOD)
    fn(records)
    return records


def add_class(records, name, inherit, target_type="Capability specification document"):
    """A second requirements class with one requirement, test and conformance class."""
    records += [
        {"kind": "requirements_class", "id": f"/req/{name}", "subject": target_type, "inherit": inherit,
         "requirements": [f"/req/{name}/r"]},
        {"kind": "requirement", "id": f"/req/{name}/r", "statement": "X SHALL Y."},
        {"kind": "abstract_test", "id": f"/conf/{name}/r", "target": f"/req/{name}/r", "purpose": "p"},
        {"kind": "conformance_class", "id": f"/conf/{name}", "target": f"/req/{name}", "tests": [f"/conf/{name}/r"]},
    ]


class SpecRuleTests(unittest.TestCase):
    def test_good_set_is_clean(self):
        code, found, summary = rules(GOOD)
        self.assertEqual((code, found), (0, []))
        self.assertIn("M007", summary["rules_run"])

    def test_recommendation_without_test_is_not_a_finding(self):
        self.assertNotIn("M007", rules(GOOD)[1])

    def test_untested_requirement(self):
        _, found, _ = rules(mutate(lambda r: r.pop(3)))
        self.assertIn("M007", found)

    def test_unknown_kind(self):
        _, found, _ = rules(mutate(lambda r: r.append({"kind": "mystery", "id": "/x"})))
        self.assertIn("G001", found)

    def test_missing_identifier(self):
        _, found, _ = rules(mutate(lambda r: r.append({"kind": "requirement", "statement": "X SHALL Y."})))
        self.assertIn("M001", found)

    def test_duplicate_identifier(self):
        _, found, _ = rules(mutate(lambda r: r.append(copy.deepcopy(r[1]))))
        self.assertIn("M001", found)

    def test_requirement_listed_by_no_class(self):
        _, found, _ = rules(mutate(lambda r: r[0].update(requirements=[])))
        self.assertIn("M002", found)

    def test_requirement_listed_by_two_classes(self):
        def change(r):
            add_class(r, "ext", ["/req/core"])
            r[5]["requirements"].append("/req/core/valid-document")
        _, found, _ = rules(mutate(change))
        self.assertIn("M002", found)

    def test_membership_is_by_listing_not_by_identifier_prefix(self):
        # the class is named unlike its members, as in ModSpec Part 1 itself: still clean
        def change(r):
            r[0]["id"] = "/req/req-class-core"
            r[4]["target"] = "/req/req-class-core"
            r[4]["id"] = "/conf/conf-class-core"
        code, found, _ = rules(mutate(change), CONFIG.replace('"/req/core"', '"/req/req-class-core"'))
        self.assertEqual((code, found), (0, []))

    def test_listed_requirement_not_defined(self):
        _, found, _ = rules(mutate(lambda r: r[0]["requirements"].append("/req/core/ghost")))
        self.assertIn("M003", found)

    def test_missing_target_type(self):
        _, found, _ = rules(mutate(lambda r: r[0].pop("subject")))
        self.assertIn("M004", found)

    def test_test_target_not_a_requirement(self):
        _, found, _ = rules(mutate(lambda r: r[3].update(target="/req/core/ghost")))
        self.assertIn("M008", found)

    def test_conformance_class_missing(self):
        _, found, _ = rules(mutate(lambda r: r.pop(4)))
        self.assertIn("M005", found)

    def test_two_conformance_classes_for_one_class(self):
        _, found, _ = rules(mutate(lambda r: r.append({**r[4], "id": "/conf/core-again"})))
        self.assertIn("M005", found)

    def test_conformance_class_target_unknown(self):
        _, found, _ = rules(mutate(lambda r: r[4].update(target="/req/ghost")))
        self.assertIn("M005", found)

    def test_conformance_class_missing_a_test(self):
        _, found, _ = rules(mutate(lambda r: r[4].update(tests=[])))
        self.assertIn("M006", found)

    def test_conformance_class_lists_a_test_of_another_class(self):
        def change(r):
            add_class(r, "ext", ["/req/core"])
            r[4]["tests"].append("/conf/ext/r")
        _, found, summary = rules(mutate(change))
        self.assertIn("M006", found)
        self.assertTrue(any("not a requirement of" in f["message"] for f in summary["findings"]))

    def test_uncovered_requirements_are_one_finding_per_conformance_class(self):
        def change(r):
            for i in range(5):
                r[0]["requirements"].append(f"/req/core/r{i}")
                r.append({"kind": "requirement", "id": f"/req/core/r{i}", "statement": "X SHALL Y."})
        _, _, summary = rules(mutate(change))
        m006 = [f for f in summary["findings"] if f["rule"] == "M006"]
        self.assertEqual(len(m006), 1)
        self.assertIn("uncovered:5", m006[0]["key"])

    def test_unresolved_relative_inherit(self):
        _, found, _ = rules(mutate(lambda r: r[0].update(inherit=["/req/nowhere"])))
        self.assertIn("M009", found)

    def test_undeclared_external_inherit_is_found_when_references_are_declared(self):
        _, found, _ = rules(mutate(lambda r: r[0].update(inherit=["http://example.org/other/conf/core"])))
        self.assertEqual(found, ["M009"])

    def test_external_inherit_is_not_checked_when_no_references_are_declared(self):
        cfg = 'records_dir = "records"\ncore = "/req/core"\n'
        code, found, _ = rules(mutate(lambda r: r[0].update(inherit=["http://example.org/other/conf/core"])), cfg)
        self.assertEqual((code, found), (0, []))

    def test_inherit_by_class_title_resolves(self):
        def change(r):
            r[0]["title"] = "Core"
            add_class(r, "ext", ["Core"])
        code, found, _ = rules(mutate(change))
        self.assertEqual(found, [])

    def test_dependency_cycle(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            add_class(r, "b", ["/req/a", "/req/core"])
            r[5]["inherit"].append("/req/b")
        _, found, summary = rules(mutate(change))
        self.assertIn("M010", found)

    def test_core_must_be_defined(self):
        _, found, _ = rules(GOOD, CONFIG.replace('"/req/core"', '"/req/missing"', 1))
        self.assertIn("M011", found)

    def test_non_core_class_must_inherit_core_directly(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            add_class(r, "b", ["/req/a"])  # transitive only
        _, found, summary = rules(mutate(change))
        self.assertEqual(found, ["M012"])
        self.assertEqual([f["key"] for f in summary["findings"]], ["/req/b>transitive"])
        self.assertIn("literal reading", summary["findings"][0]["clause"])

    def test_transitive_mode_accepts_a_chain_but_not_an_unreachable_class(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            add_class(r, "b", ["/req/a"])
            add_class(r, "c", [])
        cfg = 'core_dependency = "transitive"\n' + CONFIG
        _, _, summary = rules(mutate(change), cfg)
        self.assertEqual([f["key"] for f in summary["findings"] if f["rule"] == "M012"], ["/req/c>unreachable"])

    def test_core_rules_do_not_run_without_a_core(self):
        _, _, summary = rules(GOOD, 'records_dir = "records"\n')
        self.assertIn("M011", summary["rules_not_run"])
        self.assertNotIn("M012", summary["rules_run"])


class NamespaceTests(unittest.TestCase):
    NS = "https://www.opengis.net/spec/x-1/1.0"

    def with_ns(self, fn=None):
        def change(r):
            r[0]["id"] = f"{self.NS}/req/core"
            r[4]["id"] = f"{self.NS}/conf/core"
            r[4]["target"] = f"{self.NS}/req/core"
            if fn:
                fn(r)
        return mutate(change)

    def test_absolute_and_relative_ids_are_the_same_id_when_namespace_is_configured(self):
        code, found, _ = rules(self.with_ns(), f'namespace = "{self.NS}"\n' + CONFIG)
        self.assertEqual((code, found), (0, []))

    def test_without_the_namespace_they_are_different(self):
        _, found, _ = rules(self.with_ns())
        self.assertTrue(found)

    def test_http_and_https_are_not_treated_as_equal(self):
        _, found, _ = rules(self.with_ns(), f'namespace = "{self.NS.replace("https", "http")}"\n' + CONFIG)
        self.assertTrue(found)

    def test_underscore_and_hyphen_are_not_treated_as_equal(self):
        # OGC API - Processes inherits from ogcapi_common-1; normalisation must not hide that
        def change(r):
            r[0]["inherit"] = [self.NS.replace("x-1", "x_1") + "/req/core"]
        _, found, _ = rules(self.with_ns(change), f'namespace = "{self.NS}"\n' + CONFIG)
        self.assertEqual(found, ["M009"])


class PolicyAndStyleTests(unittest.TestCase):
    def test_iso_verbal_forms_run_by_default_and_ignore_case(self):
        code, found, summary = rules(GOOD)
        self.assertEqual((code, found), (0, []))
        self.assertIn("P002", summary["rules_run"])
        lower = mutate(lambda r: r[1].update(statement="A document shall validate against the schema."))
        self.assertEqual(rules(lower)[1], [])

    def test_wrong_verbal_form_for_the_kind(self):
        _, found, _ = rules(mutate(lambda r: r[1].update(statement="A document may validate.")))
        self.assertIn("P002", found)
        _, found, _ = rules(mutate(lambda r: r[2].update(statement="Ids shall be stable.")))
        self.assertIn("P002", found)

    def test_shall_not_and_should_not_satisfy_their_kinds(self):
        records = mutate(lambda r: (r[1].update(statement="A document shall not be empty."),
                                    r[2].update(statement="Ids should not change.")))
        self.assertEqual(rules(records)[1], [])

    def test_must_and_may_not_are_flagged(self):
        _, found, summary = rules(mutate(lambda r: r[1].update(statement="A document SHALL validate and must be small.")))
        self.assertEqual(found, ["P003"])
        _, found, _ = rules(mutate(lambda r: r[2].update(statement="Ids should be stable and may not change.")))
        self.assertEqual(found, ["P003"])

    def test_empty_statement_is_p002(self):
        _, found, _ = rules(mutate(lambda r: r[1].update(statement="")))
        self.assertIn("P002", found)

    def test_project_override_and_switch_off(self):
        cfg = CONFIG + '[verbal_forms]\nrequirement = ["must"]\n'
        self.assertIn("P002", rules(GOOD, cfg)[1])
        _, _, summary = rules(GOOD, 'iso_verbal_forms = false\n' + CONFIG)
        self.assertIn("P002", summary["rules_not_run"])

    def test_prefix_style_is_off_by_default_and_on_request(self):
        def change(r):
            r[0]["id"] = "/req/req-class-core"
            r[4]["target"] = "/req/req-class-core"
        records = mutate(change)
        cfg = CONFIG.replace('"/req/core"', '"/req/req-class-core"')
        self.assertEqual(rules(records, cfg)[1], [])
        self.assertIn("S002", rules(records, 'style = ["prefix"]\n' + cfg)[1])

    def test_bad_id_shape_is_style_only(self):
        records = mutate(lambda r: r[1].update(id="/req/core/Valid Document"))
        records[0]["requirements"] = ["/req/core/Valid Document"]
        records[3]["target"] = "/req/core/Valid Document"
        self.assertEqual(rules(records)[1], [])
        self.assertIn("S001", rules(records, 'style = ["prefix"]\n' + CONFIG)[1])


class BaselineTests(unittest.TestCase):
    def test_baseline_accepts_known_finding_and_rejects_new_ones(self):
        records = mutate(lambda r: r.pop(3))
        tmp, cfg = build(records)
        with tmp:
            _, summary = gate.run(cfg, None)
            ids = sorted({f"{f['rule']}:{f['key']}" for f in summary["findings"]})
            base = cfg.parent / "baseline.json"
            base.write_text(json.dumps({"expected": ids}), encoding="utf-8")
            code, summary = gate.run(cfg, base)
            self.assertEqual(code, 0)
            self.assertEqual(summary["baseline"], {"unexpected": [], "missing": []})
            (cfg.parent / "records" / "extra.yaml").write_text(
                yaml.safe_dump({"kind": "mystery", "id": "/x"}), encoding="utf-8")
            code, summary = gate.run(cfg, base)
            self.assertEqual(code, 1)
            self.assertTrue(summary["baseline"]["unexpected"])

    def test_baseline_fails_when_an_expected_finding_disappears(self):
        tmp, cfg = build(GOOD)
        with tmp:
            base = cfg.parent / "baseline.json"
            base.write_text(json.dumps({"expected": ["M007:/req/core/gone"]}), encoding="utf-8")
            code, summary = gate.run(cfg, base)
            self.assertEqual(code, 1)
            self.assertEqual(summary["baseline"]["missing"], ["M007:/req/core/gone"])

    def test_every_rule_has_a_basis_and_a_source_and_no_spec_rule_is_unconfirmed(self):
        for rule, (description, basis, source) in gate.RULES.items():
            self.assertTrue(description and source, rule)
            self.assertIn(basis, {"spec", "policy", "style", "structure", "stage2"}, rule)
            if basis in ("spec", "policy"):
                self.assertNotIn("unconfirmed", source, rule)


def with_profile(records, inherit=("/req/core", "/req/a"), **extra):
    """GOOD plus a class /req/a (inherits the core) and a profile /req/prof built on `inherit`."""
    add_class(records, "a", ["/req/core"])
    records += [
        {"kind": "requirements_class", "id": "/req/prof", "subject": "Capability specification document",
         "profile": True, "inherit": list(inherit), "requirements": []},
        {"kind": "conformance_class", "id": "/conf/prof", "target": "/req/prof", "tests": []},
    ]
    for record in records:
        if record["id"] in ("/req/prof", "/conf/prof"):
            record.update(extra.get(record["id"], {}))
    return records


def build_files(files, config):
    """files: {relative path: record or list of records}. Returns (TemporaryDirectory, config path)."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "ogcspec.gate.toml").write_text(config, encoding="utf-8")
    for name, content in files.items():
        target = root / "records" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(content), encoding="utf-8")
    return tmp, root / "ogcspec.gate.toml"


class RecordFormatTests(unittest.TestCase):
    """Plan step 2/3: fields added by record-format-proposal.md and the rules about them."""

    def keys(self, summary, rule):
        return sorted(f["key"] for f in summary["findings"] if f["rule"] == rule)

    def test_misspelled_field_is_g002_and_names_the_near_miss(self):
        records = mutate(lambda r: r[0].update({"requirments": ["/req/core/valid-document"]}))
        _, found, summary = rules(records)
        self.assertIn("G002", found)
        self.assertEqual(self.keys(summary, "G002"), ["/req/core#requirments"])
        self.assertIn("'requirements'", summary["findings"][[f["rule"] for f in summary["findings"]].index("G002")]["message"])

    def test_inherit_on_a_conformance_class_is_g002_and_points_to_depends_on(self):
        records = mutate(lambda r: r[4].update({"inherit": ["/conf/x"]}))
        _, _, summary = rules(records)
        message = next(f["message"] for f in summary["findings"] if f["rule"] == "G002")
        self.assertIn("depends_on", message)

    def test_status_and_internal_keys_are_not_unknown_fields(self):
        records = mutate(lambda r: [x.update({"status": "proposed"}) for x in r])
        self.assertEqual(rules(records)[:2], (0, []))

    def test_bad_values_are_g003(self):
        def change(r):
            r[0].update({"status": "approved", "profile": "yes", "uml_package": "", "title": 3})
            r[4]["depends_on"] = "/conf/x"
        _, found, summary = rules(mutate(change))
        self.assertIn("G003", found)
        self.assertEqual(self.keys(summary, "G003"),
                         ["/conf/core#depends_on", "/req/core#profile", "/req/core#status", "/req/core#title", "/req/core#uml_package"])

    def test_field_rules_do_not_run_on_records_rebuilt_from_xml(self):
        record = {"kind": "conformance_class", "id": "/conf/core", "target": "/req/core", "tests": [], "inherit": ["/conf/x"],
                  "_file": "doc.xml", "_anchor": "a"}
        found, not_run = gate.check([record], {})
        self.assertNotIn("G002", {f.rule for f in found})
        self.assertIn("G002", not_run)

    def test_depends_on_naming_a_class_of_this_document_is_g004(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            r[-1]["depends_on"] = ["/conf/core"]
        _, found, summary = rules(mutate(change))
        self.assertEqual(found, ["G004"])
        self.assertEqual(self.keys(summary, "G004"), ["/conf/a>/conf/core"])

    def test_external_depends_on_resolves_against_declared_references(self):
        ok = mutate(lambda r: r[4].update({"depends_on": [DEP]}))
        self.assertEqual(rules(ok)[:2], (0, []))
        bad = mutate(lambda r: r[4].update({"depends_on": ["https://example.org/elsewhere/conf/x"]}))
        self.assertEqual(rules(bad)[1], ["M014"])
        relative = mutate(lambda r: r[4].update({"depends_on": ["/conf/missing"]}))
        self.assertEqual(rules(relative)[1], ["M014"])

    def test_external_depends_on_is_not_checked_when_no_references_are_declared(self):
        records = mutate(lambda r: r[4].update({"depends_on": ["https://example.org/elsewhere/conf/x"]}))
        self.assertEqual(rules(records, 'core = "/req/core"\n')[1], [])

    def test_a_profile_built_from_existing_kinds_is_clean(self):
        code, found, _ = rules(with_profile(copy.deepcopy(GOOD)))
        self.assertEqual((code, found), (0, []))

    def test_profile_with_requirements_tests_or_no_base_is_m013(self):
        own_requirement = with_profile(copy.deepcopy(GOOD), **{"/req/prof": {"requirements": ["/req/core/valid-document"]}})
        self.assertIn("M013", rules(own_requirement)[1])
        own_tests = with_profile(copy.deepcopy(GOOD), **{"/conf/prof": {"tests": ["/conf/core/valid-document"]}})
        self.assertIn("M013", rules(own_tests)[1])
        no_base = with_profile(copy.deepcopy(GOOD), inherit=())
        _, found, summary = rules(no_base)
        self.assertIn("M013", found)
        self.assertEqual(self.keys(summary, "M013"), ["/req/prof>inherit"])

    def test_profile_that_builds_only_on_a_non_core_class_meets_the_literal_core_rule_only_in_transitive_mode(self):
        records = with_profile(copy.deepcopy(GOOD), inherit=("/req/a",))
        _, found, summary = rules(records)
        self.assertEqual(found, ["M012"])
        self.assertEqual(self.keys(summary, "M012"), ["/req/prof>transitive"])
        self.assertEqual(rules(records, 'core_dependency = "transitive"\n' + CONFIG)[1], [])

    def test_profile_marker_changes_nothing_for_other_classes(self):
        records = mutate(lambda r: r[0].update({"profile": False}))
        self.assertEqual(rules(records)[:2], (0, []))

    def test_uml_package_rules_are_off_by_default_and_opt_in(self):
        records = mutate(lambda r: add_class(r, "a", ["/req/core"]))
        _, found, summary = rules(records)
        self.assertEqual(found, [])
        self.assertIn("S003", summary["rules_not_run"])
        _, found, summary = rules(records, 'style = ["uml"]\n' + CONFIG)
        self.assertEqual(found, ["S003"])
        self.assertEqual(self.keys(summary, "S003"), ["/req/a", "/req/core"])

    def test_two_classes_naming_one_uml_package_is_s004(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            r[0]["uml_package"] = r[-4]["uml_package"] = "example::shared"
        _, found, summary = rules(mutate(change), 'style = ["uml"]\n' + CONFIG)
        self.assertEqual(found, ["S004"])
        self.assertEqual(self.keys(summary, "S004"), ["example::shared"])

    def test_distinct_uml_packages_are_clean(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            r[0]["uml_package"], r[-4]["uml_package"] = "example::core", "example::a"
        self.assertEqual(rules(mutate(change), 'style = ["uml"]\n' + CONFIG)[:2], (0, []))

    def layout_files(self, records, wrong=None):
        files = {}
        for r in records:
            name = r["id"].lstrip("/") + ".yaml"
            files[(wrong or {}).get(r["id"], name)] = r
        return files

    def test_layout_rule_accepts_path_following_id(self):
        tmp, cfg = build_files(self.layout_files(GOOD), 'style = ["layout"]\n' + CONFIG)
        with tmp:
            code, summary = gate.run(cfg, None)
        self.assertEqual((code, summary["findings"]), (0, []))

    def test_layout_rule_reports_a_wrong_path_and_a_shared_file(self):
        files = self.layout_files(GOOD, wrong={"/rec/core/stable-ids": "misc/other.yaml"})
        del files["conf/core/valid-document.yaml"]  # the test now shares the requirement's file
        files["req/core/valid-document.yaml"] = [GOOD[1], GOOD[3]]
        tmp, cfg = build_files(files, 'style = ["layout"]\n' + CONFIG)
        with tmp:
            _, summary = gate.run(cfg, None)
        self.assertEqual(sorted(f["key"] for f in summary["findings"] if f["rule"] == "S005"),
                         ["/conf/core/valid-document#path", "/rec/core/stable-ids#path", "req/core/valid-document.yaml#records"])

    def test_layout_rule_is_off_by_default(self):
        tmp, cfg = build_files({"anything.yaml": GOOD}, CONFIG)
        with tmp:
            code, summary = gate.run(cfg, None)
        self.assertEqual((code, summary["findings"]), (0, []))
        self.assertIn("S005", summary["rules_not_run"])


class ConformanceInheritTests(unittest.TestCase):
    """The derived dependency list of a conformance class (Req 12, proposal section 4)."""

    def derive(self, records, config=""):
        return gate.conformance_inherit(records, tomllib.loads(config))

    def test_internal_dependencies_are_derived_and_external_ones_are_not(self):
        records = mutate(lambda r: add_class(r, "a", ["/req/core", DEP]))
        self.assertEqual(self.derive(records), {"/conf/core": [], "/conf/a": ["/conf/core"]})

    def test_depends_on_follows_derived_entries_and_duplicates_are_dropped(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            r[-1]["depends_on"] = [DEP, DEP, "/conf/a"]
        self.assertEqual(self.derive(mutate(change))["/conf/a"], ["/conf/core", DEP])

    def test_namespace_absolute_entries_resolve_and_the_class_id_is_written_as_the_author_wrote_it(self):
        ns = "https://www.opengis.net/spec/x-1/1.0"
        def change(r):
            r[4]["id"] = f"{ns}/conf/core"
            add_class(r, "a", [f"{ns}/req/core"])
        derived = self.derive(mutate(change), f'namespace = "{ns}"\n')
        self.assertEqual(derived["/conf/a"], [f"{ns}/conf/core"])

    def test_inherit_by_title_resolves(self):
        def change(r):
            r[0]["title"] = "Core"
            add_class(r, "a", ["Core"])
        self.assertEqual(self.derive(mutate(change))["/conf/a"], ["/conf/core"])

    def test_a_class_without_exactly_one_conformance_class_derives_nothing(self):
        def change(r):
            add_class(r, "a", ["/req/core"])
            r.append({"kind": "conformance_class", "id": "/conf/core-again", "target": "/req/core", "tests": []})
        self.assertEqual(self.derive(mutate(change))["/conf/a"], [])


if __name__ == "__main__":
    unittest.main()
