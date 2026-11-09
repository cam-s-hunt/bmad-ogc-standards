# Starting a standard in an existing repository: a rehearsed runbook

**Rehearsed 2026-11-09** in a scratch clone of an existing public repository (a project with a website, notes and examples, and no BMAD files),
with BMAD at the commit in `BMAD-PIN` and this module installed from GitHub. Nothing was pushed and the original repository was not touched.
This is what was run, in order, and every surprise. Anything not listed under "Not tested" was run.

## Steps (as run; about a minute of work plus the compile)

1. **Work in a copy or a branch first.** The install adds about 5 MB of tool files and several untracked folders (step 5).
2. **BMAD base, pinned.** Clone `bmad-code-org/BMAD-METHOD`, check out the `sha` in `BMAD-PIN` (the documented route installs BMAD's moving `main`; not tried, see below), then from the
   target repository root:
   `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 npx --yes skills@1.7.6 add <bmad clone>/skills --skill '*' --agent claude-code --copy -y`
   (35 skills, under `.claude/skills/`; about 3 seconds). It prints "Review skills before use; they run with full agent permissions."
3. **This module, from GitHub:**
   `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 npx --yes skills@1.7.6 add cam-s-hunt/bmad-ogc-standards --skill '*' --agent claude-code --copy -y`
   (7 more skills; byte-identical to `skills/` of this repository on the day of the rehearsal).
4. **Register the module** with the answers file in exactly this form (JSON and a flat `[ogcspec]` table are both rejected):
   ```toml
   [modules.ogcspec]
   ogc_doctype = "standard"
   gate_config_path = "ogcspec.gate.toml"
   decisions_dir = "docs/decisions"
   ```
   `python3 .claude/skills/bmad/scripts/setup.py --project-root . --skill .claude/skills/bmad --root .claude/skills --module-answers <answers.toml>`
   It creates `_bmad/` (config, shared scripts, the module's `gate.py`, `emit.py`, `metanorma.py` under `_bmad/ogcspec/scripts/`). `--status` then reports `current: true`, no problems, no pending questions.
   `project_name` in `_bmad/config.toml` defaults to the folder name.
5. **Ignore the generated files.** The install leaves these untracked: `.claude/`, `_bmad/`, `skills-lock.json`, and later `_bmad-output/` and `build/`. This repository's own `.gitignore` shows the entries (`.claude/skills/`,
   `skills-lock.json`, `_bmad/scripts/`, `_bmad/*/scripts/`, `_bmad-output/`); `_bmad/config.toml` and `_bmad/custom/` are meant to be shared. Note that `skills-lock.json` records the **local path** of the BMAD clone, so it
   must not be committed.
6. **The two files a first-time user writes:** a gate config (`ogcspec.gate.toml`: `records_dir`, `core`, optional `style`, `[[normative_references]]`) and a records folder. The module's worked example
   (`skills/ogcspec-modspec/references/record-format-example.yaml`, its header gives the config) passes: `uv run _bmad/ogcspec/scripts/gate.py --config ogcspec.gate.toml` read 12 records, no findings.
7. **Emit and compile.** `emit.py --records records --out build --config ogcspec.gate.toml` wrote the three fragment files (exit 0). **The module ships no master document**, so the fragments need a hand-written
   skeleton that `include::`s them (the one in `skills/ogcspec-metanorma/scripts/tests/test_emit.py` works as a starting point). `metanorma.py --image <digest from METANORMA-PIN> --adoc build/doc.adoc --formats xml`
   compiled offline (exit 0), and the installed gate's stage 2 (`--xml build/doc.xml --compile-result build/compile.json`) read the 12 records back with no fidelity findings; only Metanorma's own messages
   (X010) came through, as accepted through a baseline.
8. **Start the agent.** In Claude Code, started in the repository, "Talk to the ModSpec Architect" activated the persona (it loaded the skill, resolved its configuration from `_bmad/`, and on a read-only request ran the
   installed gate and reported findings and the rules that did not run). One session, run once; not a measure of quality.

## Surprises and gaps found (none fixed by the rehearsal itself)

- The `--module-answers` format above is documented nowhere in this module; it is BMAD's, found by reading the setup script.
- **One baseline cannot serve both stages.** A baseline that lists Metanorma's messages (X010, needed for stage 2) makes a stage-1 run exit 1, because the gate reports baselined findings that "disappeared" even
  though stage 1 cannot produce them; and the X rules do not appear under `rules_not_run` in stage 1 (the persona noticed both). Until changed, keep a separate baseline file per stage.
- No master document skeleton ships with the module (step 7).
- The generated folders are untracked until the project's `.gitignore` is edited (step 5).
- The module's setup asks three questions that already have defaults; the defaults are fine for a first run.

## Not tested

BMAD's moving `main` (the documented install route); Windows; GitHub branch protection and code-owner review (the mechanism that protects `status: accepted`); a real document header, bibliography and
terms clause; the eval harness in a target repository; more than one agent session; any network-less install.
