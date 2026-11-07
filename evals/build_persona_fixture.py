#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Build a throwaway mini-project for evaluating the persona skills (ogcspec-agent-architect, -editor).

The eval runner's clean room has none of the project's `_bmad/` scripts, which the personas call when they
activate. This script writes a small stand-in project (the BMAD config resolvers, a gate config, three
placeholder records with one planted gap, and the sibling skills the personas hand work to) so the runner
can be pointed at it with `--project-root`. The persona under test is NOT copied: the runner stages it.

Everything here is a placeholder "widget" standard; no identifier is assigned or proposed for a real standard.

Usage: build_persona_fixture.py [--out DIR]   (default: _bmad-output/persona-fixture, which is git-ignored)
Then:  uv run .claude/skills/bmad-eval/scripts/run_evals.py --project-root <DIR> --harness <harness.json> \
         --cases evals/ogcspec-agent-architect/cases.json --skill-path skills/ogcspec-agent-architect \
         --output-dir _bmad-output/eval-reports --mode quality --runs 3
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BMAD_SCRIPTS = ("resolve_config.py", "resolve_customization.py")
SIBLINGS = ("ogcspec-modspec", "ogcspec-gate", "ogcspec-review", "ogcspec-metanorma")

CONFIG = """[core]
project_name = "widget-standard-fixture"
output_folder = "{project-root}/_bmad-output"

[modules.ogcspec]
ogc_doctype = "standard"
gate_config_path = "ogcspec.gate.toml"
decisions_dir = "docs/decisions"
"""

GATE_CONFIG = """records_dir = "records"
core = "/req/core"
"""

RECORDS = """- kind: requirements_class
  id: /req/core
  title: Core
  status: proposed
  subject: Widget description
  inherit: []
  requirements:
    - /req/core/name
    - /req/core/parts

- kind: requirement
  id: /req/core/name
  status: proposed
  statement: A widget description SHALL give the widget a name.

- kind: requirement
  id: /req/core/parts
  status: proposed
  statement: A widget description SHALL list the widget's parts.

- kind: abstract_test
  id: /conf/core/name
  status: proposed
  target: /req/core/name
  purpose: Verify that a widget description names the widget.
  steps:
    - Inspect the widget description for a name.

- kind: conformance_class
  id: /conf/core
  title: Core
  status: proposed
  target: /req/core
  tests:
    - /conf/core/name
"""
# /req/core/parts has no abstract test on purpose: the gate reports it (M006/M007), which the cases use.


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    (out / "_bmad" / "scripts").mkdir(parents=True)
    (out / "_bmad" / "ogcspec" / "scripts").mkdir(parents=True)
    (out / "records").mkdir()
    (out / ".claude" / "skills").mkdir(parents=True)
    for name in BMAD_SCRIPTS:
        src = REPO / "_bmad" / "scripts" / name
        if not src.is_file():
            sys.exit(f"missing {src}: install BMAD in this repository first (see docs/HANDOFF.md)")
        shutil.copy2(src, out / "_bmad" / "scripts" / name)
    (out / "_bmad" / "config.toml").write_text(CONFIG, encoding="utf-8")
    shutil.copy2(REPO / "skills" / "ogcspec-gate" / "scripts" / "gate.py", out / "_bmad" / "ogcspec" / "scripts" / "gate.py")
    (out / "ogcspec.gate.toml").write_text(GATE_CONFIG, encoding="utf-8")
    (out / "records" / "core.yaml").write_text(RECORDS, encoding="utf-8")
    for name in SIBLINGS:
        shutil.copytree(REPO / "skills" / name, out / ".claude" / "skills" / name,
                        ignore=shutil.ignore_patterns("__pycache__", "tests"))
    print(f"fixture written to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=REPO / "_bmad-output" / "persona-fixture")
    build(parser.parse_args().out)
