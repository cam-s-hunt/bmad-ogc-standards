# Handoff (2026-11-06)

For a fresh session started in this repository. Read `CLAUDE.md` first, then `docs/PLAN.md`.

## What this is
A BMAD module (`ogcspec`) for agentic, spec-anchored development of a standard intended for OGC submission (built for
a target standard repository, to be created later). Prototype; not registered with or endorsed by OGC; no LICENSE (owner's decision).

## What exists (all tested; see README for what is and is not verified)
- `skills/ogcspec-gate/scripts/gate.py`: the canonical rule engine. Rules M (ModSpec Part 1 requirement numbers),
  P (draft Policy 25-001 + ISO Directives Part 2 cl. 7), S (opt-in house style), X (compiled-document checks).
  Stage 2 reads Metanorma's semantic XML. Differential baseline. Fails closed on a failed compile, a result that is not
  an explicit exit 0, and a document with no definitions.
- `skills/ogcspec-metanorma/scripts/`: `emit.py` (YAML records to AsciiDoc fragments, prose as literal text) and
  `metanorma.py` (digest-pinned Docker image, offline, never pulls, `--root` for documents that include files from outside
  their folder).
- `skills/ogcspec-modspec`, `ogcspec-gate`, `ogcspec-metanorma`: SKILL.md instructions and `references/`.
- `skills/ogcspec-gate/scripts/tests/corpus/`: manifest of real OGC documents, observed rule counts, and the runner.
  The OGC files themselves are not in this repo.
- `docs/references/`: 29 pinned submodule pointers (nothing cloned) and `REFERENCES.md` for documents that are not
  versioned source text. `docs/research/`: the Req 22 report and the ModSpec Parts 2-3 digest.
- Personas built 2026-11-06 from `docs/design/personas-and-workflow.md` (decisions in its "Decisions made" section):
  `ogcspec-agent-architect` (ModSpec Architect 📐), `ogcspec-agent-editor` (Metanorma Editor 📑) and `ogcspec-review`, plus
  `skills/bmod-ogcspec/roster.toml`, a `decisions_dir` setup question, module version 0.2.0 and an updated `help.md`.
  **Checked:** `init_skill.py --check --any-name`, `scan_paths.py`, `validate_manifests.py` pass; the agents' `[agent]` blocks and the
  `modules.ogcspec.*` config keys resolve through `_bmad/scripts`. **Not done:** no Smithy review lenses, no trigger or baseline eval,
  no run of either agent or of `ogcspec-review` on real records (none exist: the template's record format is plan step 2), no
  re-run of the gate/emitter test suites. `ogcspec-review` has no `customize.toml` (the approved plan listed one; omitted because no
  value in it would be read). Everything is uncommitted. The ogcspec module is installed in `.claude/skills/` (copy) and set up
  (`bmad setup`, defaults accepted); after editing `skills/`, reinstall with the same `add ... --skill '*'` command and run `bmad setup`.

## Pins
- BMAD: `BMAD-PIN` (main at `e734d3ac…`, v7 preview alpha, version string `6.13.0-next`). Not vendored; clone it by commit.
- Metanorma: `METANORMA-PIN` (image by digest; metanorma 2.5.16). A human must pull it (`docker pull` of the digest); the
  scripts never do. A previous pull failed on a missing containerd blob; the single 32-byte blob was restored by hand.
- Standards: see `corpus.toml` (commit SHAs) and `docs/references/`.

## BMAD install in this repository (2026-11-06)
Installed by the owner's decision, project scope, Claude Code only, **copied** (not symlinked) from a clone of the exact
`BMAD-PIN` commit, using `skills@1.7.6` (vercel-labs/skills, MIT) with `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1` set (whether the
CLI honours them is unchecked). All 35 skills (owner's decision: the project may need to generate code, since it is a template for future OGC standards) are in
`.claude/skills/`; a directory diff found every one identical to the pinned clone. Modules: core-tools, founder, method, toolsmith.
`bmad setup` was then run with `setup.py` from the install: no config questions were asked; it created `_bmad/` and reported
`current: true`, no problems. Its status check read each module's `bmod.toml` from GitHub `main` (read-only).
Git-ignored: `.claude/skills/`, `skills-lock.json` (its source is a vanished scratchpad path), `_bmad/scripts/`,
`_bmad/*/scripts/`, `_bmad-output/`. `_bmad/config.toml` and `_bmad/custom/` are not ignored (shareable) and are untracked.
This is **not** the documented GitHub route (`npx skills add bmad-code-org/BMAD-METHOD`, which tracks `main`), so that route
is still unverified. Our own module (`ogcspec`) is **not** registered: `bmad setup ogcspec` has not been run.
Skills installed mid-session did not appear in that session's skill list; restart Claude Code to use them.
To reproduce: fetch the pinned commit, run `add <dir> --skill '*' --agent claude-code --copy -y`, then `bmad setup`.

## Local-only material (not in git, not in any session's memory)
- `~/ogc-references/` (744 MB): downloaded standards and ontologies with `MANIFEST.md` / `manifest.tsv`
  (provenance, hashes, stated licence terms). Untrusted third-party data.
- `docs/*.pdf`: ISO/IEC Directives Part 2 ed. 9.0 (redline) and ISO/IEC 21838-2:2021. Ignored by git.
- The compiled real-document corpus lived in a session scratchpad and is gone after the session. To rebuild it, check out the
  repositories in `corpus.toml` at their SHAs, compile each `adoc` with `metanorma.py --root <repo>`, and set
  `OGCSPEC_CORPUS`. The compile commands are in `corpus.toml`.

## Decisions already made by the owner
- OGC submission is the goal; agentic spec-anchored development is also a goal; the BMAD module comes first because the
  hypothesis is that BMAD is the best way to manage agents and workflow for building a ModSpec-conformant, Metanorma-formatted spec.
- Module in a sibling repo; BMAD pinned at v7 main commit.
- No table-style requirements: this framework defines its own requirement format.
- Req 22 (transitive vs direct) is undecided; the gate reports three states and defaults to the literal text.
- No license yet.
- This repository is a **template** for BMAD-managed OGC standards and must stay free of any specific target standard. A target
  standard gets its own repository later, after the template is finished (decided 2026-11-06). References to the earlier target
  were removed from the working tree; earlier commits may still contain them.
- A GitHub remote will be created by the owner (empty repo, deploy key). Nothing is pushed until then.

## Things this project has already got wrong (do not repeat)
- Asserted an identifier-prefix convention as if it were ModSpec's. It is not in the standard.
- Claimed Requirement 28 was defined twice and missing from the XML; it is commented out in the source on purpose.
- Wrote an unchecked sentence about Records' core dependencies; verified it was false.
- Claimed `init_skill.py --check` passed; it passes only with `--any-name`.
- A conformance class pointed at the wrong requirements class was blamed on the parser; it is a source defect in Processes.
- Dropped three real Processes classes because Metanorma stores them as a definition list; now recovered and counted.

## Open questions and next steps
`docs/PLAN.md` lists the plan and the five questions for the ModSpec maintainers. Ontology alignment results (PROV-O to BFO,
SSN to BFO, W3C SSN 2023 alignment modules) are in `docs/research/ontology-alignments.md`; a first answer for the earlier
claim that no SOSA/SSN-to-BFO alignment exists: that was wrong, NCOR's SSN-to-BFO exists (and is CC0).
