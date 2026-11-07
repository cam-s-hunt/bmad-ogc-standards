---
name: ogcspec-gate
description: Run the canonical requirement-record gate and report JSON findings. Use when asked whether the standard's records are consistent or before proposing a commit.
---

Run from the standard's repository:

- Stage 1 (YAML records): `uv run {project-root}/_bmad/ogcspec/scripts/gate.py --config <gate config> --baseline <baseline.json>`
- Stage 2 adds the compiled document: append `--xml <build>/doc.xml --compile-result compile.json`
  (see `ogcspec-metanorma` for producing them).

Exit 0: findings equal the baseline (or there are none). Exit 1: any finding not in the baseline, or any
baselined finding that has disappeared. Exit 2: usage error. Output is one JSON object; report its
`findings` as they are, with each finding's `rule`, `key` and `clause`.

Rules (the table in `gate.py` gives each one's basis and source text):

- `M001`-`M012` are ModSpec Part 1 requirements, cited by requirement number: unique identifiers, each requirement
  in exactly one class by listing, one target type per class, class/conformance-class correspondence, coverage by
  abstract tests, resolvable dependencies, no dependency cycles, the core class and its direct dependents.
- `P001`-`P003` come from the ModSpec Policy (draft 25-001) and ISO/IEC Directives Part 2 clause 7: normative test
  annex; the preferred verbal form per kind; no `must` / `may not` in a provision.
- `G002`/`G003` report fields outside the table for a record's kind and wrong types or values (`status`, `profile`,
  `uml_package`, `title`, `depends_on`). `G004` is a `depends_on` entry naming a conformance class of the same document (it is
  derived). `M013` checks a profile (Req 19: no requirements or tests of its own, builds on at least one class) and `M014` that
  `depends_on` entries resolve (Req 12). These run on authored YAML records only, never on records rebuilt from compiled XML.
- `T001`-`T005` check term records (authored YAML only): a word is not defined twice, a mapping names a declared ontology
  (`[[ontologies]]`), its address starts with that ontology's prefix, its relation is one of the five words, and (only with
  `[terms] mappings = "normative"`; the default is informative) every term has a mapping. They check form only, never whether a mapping is right.
- `S001`/`S002` are house style (identifier shape, prefix membership); they run only with `style = ["prefix"]`.
  `S003`/`S004` (a UML package per requirements class, none shared) need `style = ["uml"]`, and `S005` (one record per file,
  path follows the id) needs `style = ["layout"]`.
- `X000`-`X004`, `X010` concern the compiled document: a failed compile, YAML/XML fidelity, a document that compiled
  to no definitions, and Metanorma's own log messages. Findings from the XML copy of the records have keys prefixed
  `xml:`.

The output lists `rules_run` and `rules_not_run` with reasons; say when a rule you would expect did not run.
Exit 0: findings equal the baseline (or there are none). Exit 1: any finding not in the baseline, or any baselined
finding that has disappeared. Exit 2: usage error. Report `findings` as they are, with `rule`, `key`, `basis` and
`clause`. Never edit the baseline to silence a finding without a human decision.
