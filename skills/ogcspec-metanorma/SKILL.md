---
name: ogcspec-metanorma
description: Render requirement records to Metanorma AsciiDoc and compile with a pinned local Docker image. Use when asked to build or check the Metanorma document.
---

# Build and check the Metanorma document

Run these from the standard's repository. `{skill-scripts}` is `{project-root}/_bmad/ogcspec/scripts`;
the image is the digest the project pinned for its builds (`repo@sha256:...`); the project records it in its own pin file.

1. **Emit** the AsciiDoc fragments from the records:
   `uv run {skill-scripts}/emit.py --records <records_dir> --out <build dir> --config <gate config>`
   It writes `conformance-classes.adoc`, `requirements.adoc` and `abstract-tests.adoc`, which the
   project-owned document `include::`s. Same records give the same bytes. It refuses a record kind it does
   not know instead of dropping it. `--config` is read only for `namespace`; pass it, because the emitter derives each
   conformance class's `inherit::` lines from its requirements class's `inherit` and must match identifiers the way the
   gate does. Class titles are written as literal block titles. `status`, `uml_package` and `profile` are not written.
   With `term` records it also writes `terms.adoc` (only then). The document must `include::terms.adoc[]` **inside its own terms
   clause, and that clause must be marked `[heading=terms and definitions]` above its title**: without it Metanorma does not
   recognise the clause and the compile aborts (STANDOC_25). Metanorma's OGC flavour adds its own boilerplate paragraphs at the top
   of that clause; hand-written terms may sit beside the emitted ones, and the gate ignores terms the records do not define. A
   mapping becomes a note "Mapping (<relation>): <address>"; a mapping's own `note` is not emitted.
2. **Compile**:
   `uv run {skill-scripts}/metanorma.py --image <repo@sha256:...> --adoc <doc.adoc> --formats xml > compile.json`
   If the document includes files from outside its own folder, add `--root <a directory containing them all>`;
   without it Asciidoctor aborts with "illegal reference to ancestor of jail".
   Exit 3 means Docker or the pinned image is missing locally. The script never pulls; tell the user and stop.
3. **Check** (`ogcspec-gate`) with stage 2:
   `uv run {skill-scripts}/gate.py --config <gate config> --baseline <baseline.json> --xml <build>/doc.xml --compile-result compile.json`

## What the compile does and does not tell you

Observed on the pinned image (table and caveats in `references/observed-behaviour.md`):

- Compiler exit 0 does not mean the document is sound: an untested requirement and a dangling `inherit`
  both exit 0. Only the gate's findings count.
- A duplicate identifier aborts the compile (exit 1, `doc.xml.abort`, no `doc.xml`). The gate reports that as
  X000; it is a failure, not an empty document.
- Metanorma's own log messages (`MODSPEC_*`, `STANDOC_*`, `OGC_*`) come through as X010 findings and are
  accepted only via the baseline. The wrapper runs the container with `--network none` so the message set is the same on every machine. Several fire on clean documents (for example `MODSPEC_1` on recommendations
  and permissions), so do not treat a message as a defect without reading it.

## Compile in a copy

Compiling inside a standard's own repository rewrote tracked files in the ModSpec clone (the compiled XML and the
`relaton/cache`). Compile a copy of the repository, or check `git status` afterwards.

## Do not

- Edit generated `.adoc` fragments; change the YAML records and re-emit.
- Pull or update the image, or change the pin, without the user's say-so.
- Report the build as passing unless the gate exited 0 against its baseline. If the image was missing and the
  round-trip test skipped, say that the emitter's output was not shown to compile.
