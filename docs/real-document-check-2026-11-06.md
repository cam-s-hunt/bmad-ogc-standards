# The gate against real OGC documents (2026-11-06)

This replaces the first version of this file, which was written after reading one compiled document and
contained two errors (see "Corrections"). Everything below was produced by compiling the documents with the
pinned image (`METANORMA-PIN`, offline) and running `gate.py` stage-2 rules over the XML. The documents are not
stored here; `skills/ogcspec-gate/scripts/tests/corpus/corpus.toml` names each repository and commit, and
`corpus/observed-2026-11-06.json` holds the counts. Counts are observations of those commits, not verdicts on the
standards: a draft such as Processes Part 1 v2.0 is expected to have inconsistencies.

## What ModSpec actually requires (read, 08-131r7 and the ModSpec Policy 25-001)

- Membership is by listing: "Each requirement ... SHALL be associated with exactly one requirements class"
  (Req 28, ATS 15). No identifier-prefix rule exists anywhere in the core requirements.
- Identifiers: Req 2 asks for a unique identifier or label for every component; clause 5 says requirements are
  denoted by partial URIs relative to the document's namespace. The Policy (25-001) says each component SHALL have
  a unique URI conformant with the Naming Authority's policies.
- The Policy is a DRAFT (status Draft, edition 1.1.0, received 2026-03-07). It mandates ModSpec for any new OGC
  Standard or revision, and for abstract specifications that have requirements; Community Standards may or may not
  follow it; a non-compliant candidate needs a TC vote as an exception. It requires the Abstract Test Suite in a
  normative annex for implementation standards, and points to ISO/IEC Directives Part 2 clause 7 for verbal forms.
- ISO/IEC Directives Part 2 clause 7 was first unreadable (iso.org returns 403 to automated fetches), then read from
  a copy the owner supplied (edition 9.0, 2021-05, redline). The gate now applies it by default (P002, P003).
- Observed in the corpus, not specified: ModSpec's own provisions use `SHALL` (uppercase), OGC API - Processes
  uses `SHALL`, the Connected Systems source uses lowercase `shall` in free text.

## Corrections to the first version

1. Requirement 28 is not "defined in two files and absent from the XML". The source comments its definition out
   ("Temporarily remove until metanorma numbering issue fixed") and shows it in a table, so it is not a Metanorma
   requirement element. A fresh compile reproduced the committed XML's 70 records exactly, so the committed XML
   is not stale and the dangling-test and untested-requirement findings stand.
2. The rules G002/G004/G007/G008/G012 described an identifier-prefix layout as if it were ModSpec's. It is not in
   the standard. It is now the opt-in `style = ["prefix"]` group (S001, S002).

## Counts per rule per document

Rule ids are in `gate.py` `RULES`, each with its basis (spec / policy / style) and source text. "-" = not compiled.

| rule | modspec-1 | processes-1 (draft 2.0) | records-1 | csapi-1 | csapi-2 | features-1 |
|---|---|---|---|---|---|---|
| records extracted | 70 | 374 | 290 | 244 | 284 | - |
| M001 id missing/duplicate | 0 | 2 | 5 | 0 | 0 | |
| M002 requirement not in exactly one class | 0 | 8 | 2 | 0 | 0 | |
| M003 listed but undefined | 1 | 0 | 0 | 1 | 0 | |
| M005 class/conformance class correspondence | 0 | 9 | 6 | 0 | 0 | |
| M006 conformance class coverage (per class) | 1 | 56 | 5 | 0 | 0 | |
| M007 requirement without a test | 1 | 24 | 11 | 0 | 0 | |
| M008 test targets no requirement | 2 | 7 | 11 | 7 | 0 | |
| M010 dependency cycle | 0 | 1 | 1 | 0 | 0 | |
| M012 non-core class not inheriting core directly | 0 | 4 | 15 | n/a | n/a | |
| P002 no preferred verbal form | 0 | 0 | 2 | 2 | 0 | |
| P003 uses `must` or `may not` | 0 | 0 | 1 | 2 | 0 | |
| X000 compile failed | | | | | | 1 |

M009 (a relative inherit target that is not a class of the document) is 0 in every compiled document; M011 and M012
run only where a core is configured (not for the Connected Systems documents, which name none).

M012 has three states, since Req 22 B says the core must be a *direct* dependency and the sources do not settle
whether a chain counts (see `docs/research/Req22-transitive-dependency.md`): of Records' 15, 6 reach the core only
through other classes and 9 never reach it; of Processes' 4, 3 and 1. Across 12 approved documents the research agent
counted 160 non-core classes: 76 list the core directly, 28 reach it only through another class, 36 do not reach it
at all, 19 reach it only through "indirect prerequisite" links, 1 lists it conditionally; only Features Part 1 passes
the literal reading everywhere. `core_dependency = "transitive"` accepts a chain. The default stays literal because
that is the text; the question for the maintainers is in the report.

## What the numbers mean

- Independent check of the extractor: Metanorma's own MODSPEC_1 (requirement with no test) and the gate's M007
  name exactly the same requirements in every document: 1/1, 24/24, 11/11, 0/0, 0/0. Two implementations
  written separately agree.
- The same comparison for dependencies (MODSPEC_2 vs unresolved inherit) agrees exactly only for CS API Part 2
  (9/9). Elsewhere Metanorma reports more, and the differences I understand are: (a) Metanorma reports `/req/core`
  as "outside this document" when classes are identified by absolute URI but inherit by relative id (4 classes in
  Processes), which the explicit `namespace` setting resolves; (b) Metanorma also reports "indirect prerequisites"
  cited inside requirement text (CS API Part 1 `/req/advanced-filtering`), which the gate does not model. Four
  Records classes (autodiscovery, crawlable-catalog, local-resources-catalog and its filtering class) are
  Metanorma-only and I have not diagnosed why.
- Defects found that are not parser artefacts (Processes Part 1 v2.0, a draft): six conformance classes (json,
  html, job-list, callback, dismiss, kvp-execute) point their `subject::` xref at `rc_core` instead of their own
  class, which is why M005/M006 are high; one abstract test carries the identifier `/conf/core`, duplicating the
  conformance class; Processes' `html` class lists itself as a dependency (`inherit:: /req/html`) and Records'
  `oas30` class has an xref to its own anchor labelled "OpenAPI Specification 3.0" (both M010); several requirement ids differ between the class list and the definition
  (`pl-limit-definition` vs `process-list-limit-definition`; `exception_results-not-available` vs
  `exception-results-not-available`); OGC API - Common is cited as `ogcapi_common-1` (underscore) in one inherit.
- ModSpec Part 1: ATS 15 targets `/req/core/req-in-only-one-req-class`, which no requirement defines (M008);
  `/req/core/conf-class-test-req-class` has no abstract test (M007); Req 28 is outside the Metanorma structure
  (M003). The class has no `subject` in the AsciiDoc but carries a classification `target-type`, which the
  extractor reads.
- OGC API - Features Part 1 (17-069) does not compile with the pinned toolchain (Ruby NoMethodError in
  `Metanorma::Utils::LineStatus#process`, metanorma-utils 2.0.11), and in any case writes requirements as tables,
  not as Metanorma requirement blocks. The gate reports the failed compile (X000) and, for a document that
  compiles to nothing, X004. Table-style requirements are not parsed.

## Shapes the extractor had to learn from real documents

A class whose `inherit` cites a bibliography item (an `eref`) compiles to a plain definition list inside `description`
with no `identifier` element (three Processes classes: oas, oas30, oas31). The extractor recovers the fields from that
list and counts the recovery in `notes`; before that fix it silently dropped them, which inflated M002 and M005.

Free-body requirement text (a `description` element, not a `part` component); `conditions` components; conformance
classes linked to their requirements class by `subject` holding an xref (anchor, not identifier); target type in
`subject` or in a `Target Type` classification; class-level shorthand elements with an anchor and no identifier
(counted, not records); `inherit` naming a class by its title or by a bare citation. Document includes that climb out
of the document's folder need `--root` on the wrapper.

## Compile side effects

Compiling inside a standard's own repository rewrote tracked files in the ModSpec clone (the compiled XML and the
`relaton/cache`). CI should compile in a copy or fail on a dirty tree afterwards.

## Not established

- Parts 2 (UML) and 3 (XML) of ModSpec were not read.
- Whether in-force standards' routine departures from a literal rule (M012, M002 in Records) mean the rule is
  mis-read or the standards are non-compliant.
- The Connected Systems documents depend on SensorML 3.0 and SWE Common 3.0 requirement classes and on
  `sensorml/2.1` conformance classes; those were not available to resolve against.
