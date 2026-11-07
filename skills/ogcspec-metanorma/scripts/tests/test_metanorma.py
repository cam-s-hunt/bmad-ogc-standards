import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "metanorma.py"
spec = importlib.util.spec_from_file_location("metanorma_wrapper", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules["metanorma_wrapper"] = mod
spec.loader.exec_module(mod)

DIGEST = "metanorma/metanorma@sha256:" + "a" * 64


class MetanormaWrapperTests(unittest.TestCase):
    def adoc(self):
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "doc.adoc"
        path.write_text("= T\n", encoding="utf-8")
        return tmp, path

    def test_tag_instead_of_digest_is_a_usage_error(self):
        tmp, path = self.adoc()
        with tmp:
            self.assertEqual(mod.main(["--image", "metanorma/metanorma:latest", "--adoc", str(path)]), 2)

    def test_missing_image_exits_3_and_never_pulls(self):
        tmp, path = self.adoc()
        with tmp, mock.patch.object(mod.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=1)
            self.assertEqual(mod.main(["--image", DIGEST, "--adoc", str(path)]), 3)
            for call in run.call_args_list:
                self.assertNotIn("pull", call.args[0])

    def test_command_uses_agree_to_terms_and_ogc_flavor(self):
        _, path = self.adoc()
        command = mod.build_command(DIGEST, path, "xml")
        self.assertIn("--agree-to-terms", command)
        self.assertEqual(command[command.index("-t") + 1], "ogc")

    def test_default_mounts_the_documents_folder_and_compiles_it_by_name(self):
        _, path = self.adoc()
        command = mod.build_command(DIGEST, path, "xml")
        self.assertEqual(command[-1], path.name)
        self.assertIn(f"{path.parent.resolve()}:/work", command)

    def test_root_sets_mount_and_working_directory_and_passes_a_relative_path(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "core" / "standard").mkdir(parents=True)
            doc = root / "core" / "standard" / "d.adoc"
            doc.write_text("= T\n", encoding="utf-8")
            command = mod.build_command(DIGEST, doc, "xml", root=root)
            self.assertIn(f"{root.resolve()}:/work", command)
            self.assertEqual(command[command.index("-w") + 1], "/work")
            self.assertEqual(command[-1], "core/standard/d.adoc")

    def test_root_that_does_not_contain_the_document_is_a_usage_error(self):
        import tempfile
        _, path = self.adoc()
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(mod.main(["--image", DIGEST, "--adoc", str(path), "--root", t]), 2)


if __name__ == "__main__":
    unittest.main()
