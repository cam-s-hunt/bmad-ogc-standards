"""Run the gate over the real OGC documents named in corpus/corpus.toml and compare with the counts observed
on 2026-11-06. SKIPS (loudly) unless OGCSPEC_CORPUS points at a directory holding those repositories with
their compiled XML; see corpus/corpus.toml. A skipped run says nothing about the extractor on real documents."""
import importlib.util
import json
import os
import sys
import tomllib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_corpus", HERE / "corpus" / "run_corpus.py")
rc = importlib.util.module_from_spec(spec)
sys.modules["run_corpus"] = rc
spec.loader.exec_module(rc)

ROOT = Path(os.environ["OGCSPEC_CORPUS"]) if os.environ.get("OGCSPEC_CORPUS") else None
MANIFEST = {d["name"]: d for d in tomllib.loads((HERE / "corpus" / "corpus.toml").read_text())["document"]}
OBSERVED = {d["name"]: d for d in json.loads((HERE / "corpus" / "observed-2026-11-06.json").read_text())["documents"]}


@unittest.skipUnless(ROOT and ROOT.is_dir(), "SKIPPED: OGCSPEC_CORPUS not set; real-document check not run")
class CorpusTests(unittest.TestCase):
    def results(self):
        return {name: rc.analyse(ROOT, doc) for name, doc in MANIFEST.items()}

    def test_counts_match_the_observed_snapshot(self):
        for name, result in self.results().items():
            with self.subTest(name):
                self.assertEqual(result.get("records"), OBSERVED[name]["records"])
                self.assertEqual(result["rules"], OBSERVED[name]["rules"])

    def test_metanorma_and_the_gate_agree_on_which_requirements_have_no_test(self):
        for name, result in self.results().items():
            if "agreement" not in result:
                continue
            with self.subTest(name):
                a = result["agreement"]
                self.assertEqual((a["MODSPEC_1_not_M007"], a["M007_not_MODSPEC_1"]), ([], []))

    def test_a_document_that_does_not_compile_fails_closed(self):
        result = self.results()["features-1"]
        self.assertEqual(result["rules"], {"X000": 1})


if __name__ == "__main__":
    unittest.main()
