# Assumptions and plan (updated 2026-11-06, after reading ModSpec, the draft Policy, ISO/IEC Directives Part 2 cl. 7 and ModSpec Parts 2-3)

Status of every statement below is marked **read** (from a source I opened), **observed** (produced by running the pinned
tools), **inferred**, or **open**.

## What changed in our assumptions

| earlier assumption | now | basis |
|---|---|---|
| Requirement ids follow `/req/<class>/<name>` and a requirement belongs to the class whose name prefixes its id | Membership is by the class's `requirement::` list (Req 28). The prefix shape is opt-in house style (`style = ["prefix"]`) | **read** 08-131r7 Req 28, ATS 15; **observed** in ModSpec, Processes, Records, CS API |
| "SHALL" in capitals is the verbal form | ISO/IEC Directives Part 2 cl. 7: `shall`/`shall not`, `should`/`should not`, `may`; no `must`, no `may not` in a provision. The clause says nothing about case | **read** ed. 9.0 (2021-05) **redline** copy; a newer edition is **unchecked** |
| The Policy (25-001) was unread | Read. It is a **Draft**; it mandates ModSpec for new OGC Standards and for abstract specs with requirements, requires the Abstract Test Suite in a normative annex, and sends verbal forms to ISO Directives Part 2 cl. 7 | **read** |
| Req 22 "core as a direct dependency" is checkable | Text says *direct*; sources do not settle whether a chain counts; 76 of 160 non-core classes in 12 approved documents list the core directly, 28 only transitively, 36 not at all. Gate reports three states and has a `core_dependency` switch | **read** + **observed**, `docs/research/Req22-transitive-dependency.md` |
| Parts 2 and 3 might add checkable record structure | They do not. Both are plain tables: no requirement elements in their compiled XML, no test identifiers, no conformance-class URI form, no notation for tying UML packages to requirements classes | **read** + **observed**, `docs/research/modspec-parts-2-3-digest.md` |
| Table-style requirements (OGC API - Features) might need parsing | No. This project defines its own requirement format at the BMAD level and at the ModSpec record level | owner decision 2026-11-06 |
| CS API depends on SensorML/SWE Common 2.x | It depends on SensorML 3.0 and SWE Common 3.0 (and cites ModSpec 08-131r3, not r7) | **observed** in the compiled `inherit` lists |

## Facts about ModSpec worth keeping in mind

- Part 2 (24-065r1) and Part 3 (24-066r1) are approved, edition 1.1, published 2026-05-21, and call themselves
  *optional* extensions of Part 1. The draft Policy says standards SHALL comply with "the Core Standard and relevant
  Parts" without defining "relevant". **Open:** whether a modeling-language standard must follow Part 2 (UML) or Part 3 (XML).
- Neither Part covers JSON; Part 1 clause 9 says alternative mechanisms are judged "solely on the structure of their
  conformance test suite".
- Defects found, worth reporting to the ModSpec maintainers: Req 23 in the published r7 is a verbatim copy of Req 20
  (overwritten in commit b8955012, "Issue 88"); Part 3 REQ006 has REQ004's text; several Part 2/3 identifier
  mismatches (digest, section 5); ATS 15 in Part 1 targets a requirement that does not exist.
- Compiling a standard's repository in place rewrites tracked files; always compile a copy.

## Plan, in order

1. **Decide where work happens.** Develop the module in this repository (BMAD toolsmith and review skills); a separate
   target-standard repository will author a standard with the module installed, but only after the template is finished. Do not install BMAD into this repo's
   tracked tree without a `.gitignore` for the generated folders. The `npx skills add` route has never been run.
2. **Define the template's requirement record format** (this is the opportunity the no-tables decision creates): one
   YAML record per component, ModSpec kinds, listing-based membership, a `namespace`, dependency lists on both
   requirements and conformance classes (Req 12), and an explicit field for the UML-package-to-class mapping that
   ModSpec Part 2 leaves undefined. Put it in `ogcspec-modspec/references/` first, as a proposal.
   **Done 2026-11-06/07:** `skills/ogcspec-modspec/references/record-format-proposal.md` (worked example beside it; the
   owner's decisions are its "Decisions" section). Implemented in step 3.
3. **Extend the gate only where a requirement can be checked from records. Done 2026-11-07** (commits `c885300` gate,
   `a6e69d7` emitter, docs after): unknown-field and value rules (G002, G003), conformance-class dependencies derived from the
   requirements class's `inherit` with `depends_on` for external ones (G004, M014, X003), profiles (M013, `profile: true`),
   class titles emitted, opt-in `uml` and `layout` style groups (S003-S005). Req 5 needs no rule or field: it follows from
   Reqs 4, 8, 11, 15 (M004-M006). The Req 12 completeness rule was deliberately not written, because it would encode the
   contested reading (question 6) and fire on approved documents. **Closed 2026-11-07:** a baseline for the two `MODSPEC_1` messages
   Metanorma gives an empty profile (`record-format-example.baseline.json`, with a test); all six corpus documents rebuilt at their
   pinned SHAs and matching the snapshot; `accepted` protected by branch protection in the target repository (owner decision, no gate rule). Leave the rest as HUMAN review steps in the BMAD workflow. ATS 12 and ATS 19 are "inspect the document" tests, so the
   gate checks structure only.
4. **Put the questions to OGC** (list below) before encoding any contested reading as a blocking rule.
5. **Ground the vocabulary** in BFO/CCO and SOSA/SSN. Working references (inference, caveats in
   `docs/research/ontology-alignments.md`): SSN-to-BFO tag v2026-07-18 (`221c65a`, CC0, maps the 2017 SSN/SOSA against
   CCO 2024-11-06) for SOSA/SSN; PROV-to-BFO `main` `c60847a` (CC0) for PROV-O; pin BFO-2020 and CCO v2.2. The W3C
   `sosa-bfo.ttl` is a non-normative draft with a typo (`rdfs:subClassOF`) that drops its Planned Act axiom; the two SOSA
   mappings disagree on Sensor, Property, Observation, Sample and System and neither cites the other. No reasoner was run.
   Software and virtual systems are an unresolved gap: NCOR makes them material, W3C keeps them non-material.
6. **BMAD side:** design the standards-authoring personas and workflow (what a ModSpec Architect, a Metanorma editor and
   a reviewer each do, and where a human must approve: identifiers, normative wording, anything sent to OGC).
   Proposal written 2026-11-06, awaiting the owner: `docs/design/personas-and-workflow.md`.
7. **Housekeeping:** a license (owner's decision); a remote and CI (the workflow in `.github/` first ran 2026-11-07: validators passed, unit tests failed on a 3.12-only f-string
   under the runner's Python 3.11, fixed; action versions still unverified); re-run the install trial after each skill change; refresh the corpus snapshot
   when the pinned image or the pinned standards change.

## Questions for the ModSpec maintainers / OGC (not yet asked)

1. Req 22 B / ATS 22: if class C lists only class B and B lists the core, does C have the core as a direct dependency?
   If a chain is acceptable, should the wording say "direct or transitive"?
2. Req 23 in published r7 duplicates Req 20 (commit b8955012). Intended?
3. Which ModSpec Parts are "relevant" to a standard that defines a conceptual model in UML and encodings in JSON?
4. What is the URI form of a conformance class for use in Part 3 REQ004 (`appinfo`)?
5. Is a Draft Policy (25-001) already enforceable on SWG submissions, and which ISO Directives edition applies to
   clause 7?
6. Req 12: does "specify any other conformance class upon which it is dependent" cover a dependency that exists only
   because the requirements class lists another class in its dependencies?

## What is still not verified

The `npx skills add` route; CI; any ModSpec rule beyond Part 1 clause 8; ISO Directives editions after 9.0; whether the
Policy's "current" ISO edition changed clause 7; whether the SSN/PROV-to-BFO axioms are logically consistent (no reasoner was run); the BMAD personas (built 2026-11-06; never run on real records, no review lenses, no eval).
