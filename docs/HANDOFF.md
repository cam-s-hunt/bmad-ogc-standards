# Handoff (2026-11-06)

For a fresh session started in this repository. Read `CLAUDE.md` first, then `docs/PLAN.md`.

## What this is
A BMAD module (`ogcspec`) for agentic, spec-anchored development of a standard intended for OGC submission (built for
a target standard repository, to be created later). Prototype; not registered with or endorsed by OGC; MIT licensed (owner's decision 2026-11-07; OGC's own rules on contributed material not checked).

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
  `skills/bmod-ogcspec/roster.toml`, a `decisions_dir` setup question, module version 0.2.0 (now 0.3.0, see the record-format paragraph) and an updated `help.md`.
  **Checked:** `init_skill.py --check --any-name`, `scan_paths.py`, `validate_manifests.py` pass; the agents' `[agent]` blocks and the
  `modules.ogcspec.*` config keys resolve through `_bmad/scripts`. **Not done:** no Smithy review lenses, no trigger or baseline eval,
  no run of either agent or of `ogcspec-review` on real records (none exist; the record format is a proposal, see below), no
  re-run of the gate/emitter test suites. `ogcspec-review` has no `customize.toml` (the approved plan listed one; omitted because no
  value in it would be read). Everything is uncommitted. The ogcspec module is installed in `.claude/skills/` (copy) and set up
  (`bmad setup`, defaults accepted); after editing `skills/`, reinstall with the same `add ... --skill '*'` command and run `bmad setup`.

- Plan step 2 (record format) and step 3 (gate and emitter) done 2026-11-06/07, decided by the owner the same day:
  `skills/ogcspec-modspec/references/record-format-proposal.md` (decisions at the end; before/after tables in sections 7 and 13),
  `record-format-example.yaml`, and the scripts `docs/design/record-format-experiment.py` and `step3-compile-tests.py`
  (reproduce the observations; both describe the tools at `b401284` and differ on later commits by design). **Implemented:**
  G002/G003 (unknown fields, values), G004 and M014 (`depends_on`), M013 (profiles via `profile: true`), S003/S004 (`uml`),
  S005 (`layout`), derived conformance-class `inherit::` (gate `conformance_inherit`, identical copy in `emit.py`, a test keeps
  them equal, X003 compares them), class titles emitted as `.pass:c[...]`, `emit.py --config`. These run on authored YAML only.
  Module version is now 0.3.0 (behaviour change: previously accepted unknown fields are G002). **Checked:** gate 96 tests, 3
  skipped (corpus); metanorma 24 tests including two round trips on the pinned image; validators pass. **Corpus:** the unit
  test needs all six documents. On 2026-11-07 it was run with all six rebuilt (Processes, Records and Features fetched with
  `git init; git fetch --depth 1 <url> <sha>; git checkout FETCH_HEAD`, exact SHAs checked, then compiled on the pinned image;
  Features does not compile, as recorded): the corpus tests pass and the gate run reports 96 tests, none skipped.
  **Baseline for the empty profile:** `record-format-example.baseline.json` (written with `--write-baseline` from a real run; keys
  carry no line numbers or paths); test `WorkedExampleBaseline` (metanorma tests: 25, none skipped). **`accepted`:** owner chose
  branch protection (code-owner review in the target repository, proposal section 8); no gate rule. Owner also kept
  `profile: true` and version 0.3.0. **Persona and review run (2026-11-07, scratch project, placeholder records):** see the next paragraph.
  **Not verified:** no agent or review lens was run on a real standard's records.
  A bug found along the way: top-level TOML keys appended after a `[[normative_references]]` table land inside it; the new
  tests and scripts put them first.
- **Persona and review run, 2026-11-07, on made-up placeholder records (a "widget description" class with two requirements; not a
  real standard).** Architect (installed skill, run by me in this session): drafted 7 files, every record `status: proposed`;
  gate stage 1 clean (S005 layout ran; `rules_not_run` printed); BUILD chain emitted, compiled on the pinned image, stage 2 gave
  only the two harness messages (`OGC_14`, `STANDOC_40`), so exit 1 without a baseline, as designed. Review (`ogcspec-review`
  -> `bmad-review`, four lenses as separate subagents that saw only the records, the one-line description and the checklist,
  so no "NOT INDEPENDENT" banner; I chose the sonnet model for them): adversarial 13, edge-case 9, structure 3 questions and no
  cuts, prose 1 optional. **What it showed:** (1) every lens flagged that each test step restates its requirement and gives no
  pass/fail criterion; the Architect's principle "write a step only from the requirement's own text" produces exactly that, so the
  principle and the review disagree and which wins is the owner's decision. (2) The Architect draft did not report gaps the
  lenses found (cardinality of a name, an empty parts list, undefined terms "widget" and "part"); the persona says a gap
  reported is worth more than one invented, so that is a miss in this run, not evidence the reviewers were wrong. (3) Padding,
  by my reading: adversarial 12 ("not a defect") and 13 (its own caveat), and parts of 9 to 11 (for example a "title" on
  abstract tests, which the record format does not have). One run, one model family, tiny records: it shows the chain works end
  to end, not that the personas or lenses are good.
- **Owner decisions 2026-11-07 (all executed):** MIT license (`LICENSE`); `backup/pre-squash` tag deleted; Architect and `ogcspec-modspec` now list what a
  restating test step leaves undecided as open questions for the owner and keep the owner's verbal form (should stays should); maintainer
  questions drafted in `docs/maintainer-questions.md` for the owner to post (nothing sent); a first eval pass ran (`docs/eval-report-2026-11-07.md`,
  cases in `evals/`; quick look only, Architect and Editor not evaluated); ontology pins in `ONTOLOGY-PINS` and `docs/research/ontology-grounding.md`
  (no mapping written: it needs a target term list). Next phase chosen by the owner: ontology grounding, which is blocked on the target's terms.
- The installed copy in `.claude/skills/` is refreshed with `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 npx --offline skills@1.7.6 add ./skills --skill '*' --agent claude-code --copy -y`
  (the package is in the npx cache); `python3 .claude/skills/bmad/scripts/setup.py --project-root . --skill .claude/skills/bmad --root .claude/skills --status`
  should report `current: true`.

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
- License: MIT (2026-11-07).
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
