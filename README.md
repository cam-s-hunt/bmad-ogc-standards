# bmad-ogc-standards

A BMAD module (`ogcspec`) for agentic, spec-anchored development of a standard intended for OGC
submission, packaged as a template for building such standards. **Status: prototype, unreleased, nothing here is registered with or
endorsed by OGC.**

## What it is

- `skills/bmod-ogcspec/` — the module record (`bmod.toml`, help). A `bmod.toml` only packages skills,
  messages and config questions. It cannot run or enforce anything.
- `skills/ogcspec-gate/` — the canonical rule engine (`scripts/gate.py`): ModSpec requirement-record checks
  as a rule table, with a differential baseline. The standard's repository vendors a released copy into its own
  CI; that CI, not an agent run, is the blocking check.
- `skills/ogcspec-metanorma/` — `emit.py` (YAML records to AsciiDoc fragments) and a wrapper that compiles with a
  local, digest-pinned Docker image. It never pulls.
- `skills/ogcspec-modspec/` — drafting skill (instructions written; verbal-form guidance deliberately absent).

## Pins and risk

- Built against BMAD `main` at the commit in `BMAD-PIN` (v7 preview alpha, unreleased, `6.13.0-next`).
  BMAD says v7 skills, install path and docs change often; expect rework when v7 ships.
- `update_source` is `github:cam-s-hunt/bmad-ogc-standards/skills`; every member skill's `source` must equal it. For a local trial, temporarily point both at a `file:` path.

## Verified so far (2026-11-06)

- BMAD's `validate_manifests.py` and `scan_scripts.py` pass at the pinned commit. `init_skill.py --check` passes
  only with `--any-name`: without it BMAD rejects every skill name that is not `bmad` or `bmad-*`, so these
  skills are accepted as third-party names, not as BMAD-namespace skills.
- Gate rules are ModSpec Part 1 requirements cited by number (M), two draft-Policy rules (P), opt-in house style (S)
  and compiled-document checks (X), plus record-structure rules (G) and, since plan step 3, rules for the added record
  fields. 96 gate tests run on 2026-11-07 with 3 skipped (the corpus tests: `OGCSPEC_CORPUS` is not set). By hand, four of the six corpus
  documents were rebuilt after the step-3 gate changes and gave the same record and rule counts as the 2026-11-06 snapshot;
  Processes, Records and the Features compile-failure case were not rebuilt. Earlier, 72 passed with the corpus enabled. The gate fails
  closed on an aborted compile, a compile result that is not an explicit exit 0, and a document with no definitions.
- Emitter round trip (records -> AsciiDoc -> pinned Metanorma, offline -> extractor) reproduces 10 records,
  comparing subject, target, statement, purpose, steps, inherit, requirements, tests and (since step 3) title and the derived
  conformance-class dependencies,
  including prose with AsciiDoc markup characters. That test skips when the pinned image is absent; a skipped
  run proves nothing about the emitter. The emitter writes prose as literal text, so emphasis and
  cross-references cannot be expressed in a record yet.
- A second install trial (fresh toy project, after `emit.py` was added) ran emit, compile and the gate from the
  installed `_bmad/ogcspec/scripts/` copies: a clean set gave no gate finding; a planted missing abstract test
  gave M006 and M007 (this trial predates the rule renaming; not re-run since). The gate fails closed on a compile result that is not an explicit exit 0.

## Not verified

- The `npx skills add` install route (only its copy step was reproduced by hand).
- Real documents: ModSpec Part 1, OGC API - Processes Part 1 (draft), Records Part 1 and Connected Systems Parts 1
  and 2 were compiled and read by the extractor; per-rule counts are in `docs/real-document-check-2026-11-06.md`
  and `tests/corpus/observed-2026-11-06.json`, and `tests/test_corpus.py` re-checks them when `OGCSPEC_CORPUS`
  points at the repositories (it skips otherwise). For untested requirements the gate and Metanorma's own
  MODSPEC_1 agree exactly; for dependencies they do not (documented). Features Part 1 crashes the pinned
  compiler and uses table-style requirements; by decision this project defines its own requirement format, so
  table-style requirements are not parsed and will not be.
- No differential baseline from a real OGC document exists, and the counts are observations, not verdicts.
- ModSpec Parts 2 (UML) and 3 (XML) were not read. Each M rule cites a requirement number of Part 1; where the text
  has two readings the rule implements the literal one (see `docs/real-document-check-2026-11-06.md`).
- Verbal forms follow ISO/IEC Directives Part 2 clause 7 as read from a local edition 9.0 (2021-05) *redline* PDF; the
  Policy links the current edition and a newer one was not checked.
- CI workflow has never run.

No LICENSE is included yet; choosing one is the owner's decision.
