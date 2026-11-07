# A `term` record kind: proposal (not implemented)

**Status: decided by the owner on 2026-11-07 (see 'Decisions' at the end). Implemented 2026-11-07: the record kind, gate rules T001-T005, the `source` and `modified` fields, emitting terms as `terms.adoc`, read-back and fidelity in stage 2 (X001/X003 by designation), tests, a real Docker round trip and a worked example (sections 9 and 10).** The owner chose option A ("add a `term` record kind") on 2026-11-07. This file is the
design for approval. **No code has changed**: the gate and the emitter still reject a `term` record (G001 unknown kind; the emitter
exits 2, see `record-format-proposal.md` section 1). Approving this file starts the work; it does not do it.

Markers as in `record-format-proposal.md`: **read** (opened for this work), **inferred** (my reasoning), **open** (the owner decides
or a test must settle it). Nothing here was checked against a real target standard, because the template has none. Ontology
facts come from `docs/research/ontology-alignments.md` and `docs/research/ontology-grounding.md`; no ontology file was parsed and
no reasoner was run.

## 1. What problem this solves

A standard defines words ("sensor", "observation", "system") and its requirements use them. Today a term has nowhere to live in the
records, so (a) its definition is hand-written Metanorma outside the generated document, and (b) a mapping to BFO/CCO or SOSA/SSN
has no home either. The pinned sources disagree on core terms and cover neither software nor virtual systems
(`ontology-grounding.md`), so any mapping is a judgement the owner must be able to see, review and change one term at a time.

## 2. The kind

One YAML record per term, like the other kinds.

| field | type | required | meaning | basis |
|---|---|---|---|---|
| `kind` | `term` | yes | discriminator | existing convention |
| `id` | string | yes | shape suggested `/term/<slug>`; a proposal for the owner to mint, never an `opengis.net` URI | **inferred**; `status` rule below |
| `term` | string | yes | the preferred designation as the standard writes it | **inferred** |
| `definition` | string | yes | the definition as the standard states it, literal text like `statement` | **inferred** |
| `aliases` | list of strings | no | admitted synonyms | **inferred** |
| `mappings` | list of mapping entries | no | links to external ontology terms (section 3). **Record-only since decision D: checked by the gate, never written into the document** | `ontology-grounding.md`, "what a target must supply" |
| `note` | string | no | free text; where the mapping is unresolved (for example software or virtual systems) say so here | **inferred** |
| `source` | bibliography key (string), or `{key, iri, label}` | no | the entry's `[SOURCE: ...]` citation; with `iri` and `label` the ontology term's address is the citation's link (`<<key, key, iri[label]>>`), exactly where the Connected Systems API puts it; the key must be an entry of the document's references | owner decisions B and D, 2026-11-07; Directives Part 2 16.5.10 |
| `modified` | `true` or `false` | no | the definition was changed from its source; needs `source` | owner decision B |
| `status` | `proposed` or `accepted` | no | same meaning and same protection as on every other kind | `record-format-proposal.md` section 8 |

Not proposed: a `normative` flag. Whether a mapping is normative or informative is a **document-level** fact in the gate config
(section 4), because one choice should apply to all terms. The research recommends informative (**read**,
`ontology-grounding.md`). **Open for the owner:** whether a term's *definition* is normative; Metanorma/OGC convention may
decide it (**open**, not looked up for this proposal).

## 3. A mapping entry

```yaml
mappings:
  - relation: close          # exact | close | broader | narrower | related
    ontology: ssn-to-bfo     # key of a declared ontology in the gate config (section 4)
    iri: "https://example.org/placeholder#Sensor"   # placeholder; must start with that ontology's iri_prefix
    note: "NCOR maps this to a BFO material entity; W3C does not (they disagree)."
```

- `relation` uses the five SKOS-style words. This is a design choice, not something the pinned sources require (**inferred**);
  the owner may prefer fewer, because each extra word is a claim somebody has to defend.
- A mapping is an assertion that someone judged two terms alike. The record states it; nothing in the toolchain can verify it
  (no reasoner has been run on the pinned ontologies).
- Several entries on one term are allowed, so a term can carry the NCOR and the W3C reading side by side and let a reviewer see
  the disagreement.

## 4. Gate config additions (document level)

Following the existing `[[normative_references]]` pattern (a `uri_prefix` that external `inherit` targets must match):

```toml
[[ontologies]]
key = "ssn-to-bfo"          # matches a section name in ONTOLOGY-PINS in this repository's convention
iri_prefix = "..."          # IRIs a mapping may use for this ontology
pin = "v2026-07-18"         # recorded for the reader; the gate does not fetch anything

[terms]
mappings = "informative"    # or "normative"; default informative
```

Adding an ontology to the config is a gate-config change, so it stays the owner's decision, as for `[[normative_references]]`.

## 5. Candidate gate rules (new prefix `T`)

| rule | check | notes |
|---|---|---|
| T001 | two terms share a `term` or alias (ignoring case), or a term repeats its own word as an alias | built; no false-positive risk |
| T002 | a mapping's `ontology` key is not declared in `[[ontologies]]` | built; mirrors the `inherit` prefix rule |
| T003 | a mapping's `iri` does not start with its ontology's `iri_prefix` | built; form only |
| T004 | `relation` outside the five words | built |
| T005 | with `[terms] mappings = "normative"` (not the default), a term has no mapping (absent or empty `mappings`) | built 2026-11-07; there is **no `unresolved` marker** yet, so this reports only absent or empty `mappings` (owner decision pending); with the default `"informative"` the rule goes to `rules_not_run` |
| (not built) | a defined term never appears in a `statement` | substring matching misfires on plurals; not built (decision 4) |
| (not built) | a capitalised word that has a record appears in prose undefined | needs a definition of "use" nobody has given; not built |

G002/G003 would extend to the new kind's fields as they do for the others. The new rules would run on authored YAML only, like
G002-G004. **Not proposed:** any rule claiming a mapping is *correct*.

## 6. Emitting the terms (the open technical question)

The emitter would have to write the terms into the document, and I have not yet found out how Metanorma's OGC flavour carries
them or whether the extractor can read them back for the round trip the other kinds have. `record-format-proposal.md` section 13
settled titles and profiles by test compiles *before* implementation; this needs the same: compile a small document with a
terms-and-definitions clause on the pinned image and look at the XML (**open**). Until then the proposal does not say how a term is
written to AsciiDoc, and the first implementation step is that experiment. If Metanorma has no clean carrier, the fallback is
that terms are record-only (checked by the gate, not emitted), which still gives the mapping table and T001-T004.

## 7. Cost and compatibility

- Additive: documents without `term` records behave exactly as before. A sensible version is 0.4.0 (**inferred**; the owner kept 0.3.0
  on the last change, so the bump is theirs to confirm).
- Touches: `gate.py` (kind, fields, rules, tests), `emit.py` only after section 6, `ogcspec-modspec/SKILL.md` (kind table), the worked
  example and its baseline file, and the corpus tests (real documents have terms, but the extractor does not read them today, so the
  corpus counts should not change; to be confirmed by running it).
- The drafting skill must not invent terms or mappings: it drafts a `term` only from a definition the owner supplies, writes no
  `mappings` without a source the owner names, and lists unresolved mappings as open questions.

## 8. Decisions for the owner

1. **Approve the kind and its fields** (section 2), or change them. In particular: `/term/<slug>` as the id shape, and whether
   `aliases` is wanted.
2. **Mapping relations:** five words, or fewer (for example `exact` and `related` only).
3. **Mapping status:** informative (recommended by the research) or normative, as the document-level default.
4. **Which rules** from section 5 are wanted; T005 and T006 are suggested off.
5. **Emit or record-only:** decided after the section 6 experiment; I would run it first and report.
6. **Version:** 0.4.0 or another.

Still needed from a target standard before any real mapping: its term list, the SOSA/SSN edition (2017 or 2023), whether software and
virtual systems are in scope, and whether definitions are normative (`ontology-grounding.md`).

## Decisions (owner, 2026-11-07)

| # | question | decision |
|---|---|---|
| 1 | Shape of the record | Approved as proposed: `/term/<slug>` ids, `aliases` kept. |
| 2 | Mapping relations | Five words: exact, close, broader, narrower, related. |
| 3 | Mapping status | First answer: **normative** (against the research note's informative recommendation, after being told the SOSA/SSN-to-BFO sources contradict each other on Sensor, Property, Observation, Sample and System). **Reversed the same day, after the owner asked how OGC does it:** the Connected Systems API (OGC 23-001, read from the local HTML copy) treats term-to-SOSA links as informative (definitions cite a source, relationships are in notes and an informative annex; SOSA addresses are binding only as values in tables such as its Table 6). **Correction, same day:** the first version of this row, and what the owner was told when deciding, said the source line was a citation to the whole ontology with no address per term. That was wrong. It came from reading the HTML copy with its tags stripped, which drops link targets. The AsciiDoc source (`api/part1/standard/sections/clause_4_terms_and_definitions.adoc`) puts a per-term address in the source citation of 10 of its 17 terms, e.g. `[.source]` `<<SOSA-SSN, SOSA/SSN, http://www.w3.org/ns/sosa/Observation[Observation Class]>>`, and the compiled XML keeps it as `<source status="identical"><origin bibitemid="SOSA-SSN"><display-text>SOSA/SSN, <link target="http://www.w3.org/ns/sosa/Observation">Observation Class</link>`. So the existing OGC practice IS a per-term machine-readable address, carried in the source citation (informative, Directives 16.5.10), not in a note to entry. The owner chose "follow the CS API pattern": mappings are **informative** by default; `[terms] mappings = "normative"` is still available and turns T005 on. The carrier in the document is a note to entry (Directives Part 2 ed. 9.0, 16.5.9 allows provisions there; not needed if informative). |
| 4 | Gate rules | T001-T004 plus a rule for a term with no mapping or an `unresolved` one (a finding the baseline may accept deliberately). T005 (defined but never used) and T006 (used but never defined) not built. |
| 5 | Emit or record-only (owner: **emit**, "build with emitting") | Experiment first (a test compile on the pinned image), then propose emit or record-only with evidence. **Run 2026-11-07; results in section 9; the emit-or-not decision is still the owner's.** |
| 6 | Version | Keep 0.3.0. |
| A | Where the mapping goes in the document | Follow the CS API pattern: a note on the entry (`Mapping (<relation>): <address>`), informative by default. |
| B | `source` field | Add `source` and a `modified` flag. |
| D | Where the ontology address goes in the document | After the dry run showed the CS API carries it in the source citation: **match OGC practice** (`source: {key, iri, label}`); `mappings` (five closeness words, several per term, per-mapping notes) stays record-only. The note-based carrier ("Mapping (<relation>): <address>") built the same day was removed. |
| C | Marker for an unresolved mapping | None; an unresolved term has no `mappings` and a `note` saying why (under normative, T005 reports it and the baseline accepts it). |

Consequence of 3: whichever status is chosen, the gate checks form only (known ontology, address prefix, relation word, and presence when
normative); nothing here claims a mapping is correct. Still open from the CS API pattern: the term's `[SOURCE: ...]` citation is not a field
yet (it would need a bibliography key; a record-format change for the owner), and the `unresolved` marker for T005 is not defined.

## 9. Experiment: how Metanorma carries terms (observed 2026-11-07, pinned image `daa12cf0...`, metanorma 2.5.16, offline)

Four hand-written test documents (a made-up "spike" header; not a real standard; kept in the session scratchpad, not in the repository),
compiled with `metanorma.py` on the pinned image. **Observed**, not inferred, unless marked.

| what I wrote | result |
|---|---|
| `== Terms and definitions` with `=== sensor`, `alt:[detector]`, a definition paragraph, a `NOTE:`, a `[.source]` reference, no extra attribute | compile **aborted** (exit 1, `doc.xml.abort`): STANDOC_25 "Clause not recognised as a term clause, but contains designation markup" |
| the same with `[heading=terms and definitions]` above the title, and the references marked `[bibliography]` | **exit 0.** Each term becomes `<term>` with `<preferred><expression><name>`, `<admitted>` for `alt:[...]`, `<definition><verbal-definition><p>`, `<termnote>` for a NOTE, and `<source><origin bibitemid=...>` for `[.source]` |
| a mapping to an ontology written as a `NOTE:` containing the address, e.g. `NOTE: Maps to https://example.org/ontology#Sensor (close).` | **clean:** a `<termnote>` with a `<link target="...">`; no term-specific message |
| a mapping written as a `[%metadata]` definition list (`mapping:: close https://...`) inside the term | compiles (exit 0), the list lands in the XML as `<dl metadata="true">` inside the `<term>`, but with STANDOC_20 ("Metadata definition list does not follow a term designation") and three STANDOC_7 schema complaints (`element "term" not allowed here`, attribute `anchor`/`id` not allowed). **Not a clean carrier.** |

Also observed: the OGC flavour inserts its own boilerplate paragraphs at the top of the terms clause (the OGC Policy Directive 49 and ModSpec
sentences), so an emitter must account for them; and `[heading=terms and definitions]` is needed for the clause to be recognised (the
spike's earlier plain "No terms." clause compiled without it only because it held no designation markup).

**What this suggests (inferred, not built):** terms *can* be emitted from records: term as the `===` heading, aliases as `alt:[...]`,
definition as a paragraph, the mapping as a fixed-form `NOTE:` (relation word plus address) that the extractor reads back from
`<termnote>`, and the clause preceded by `[heading=terms and definitions]`. Still unknown: how the emitter's fragments are spliced into
a real OGC document's existing terms clause (the boilerplate), whether the extractor can read terms back the way it reads requirements
(not written), and whether a real standard's terms clause (not my spike header) behaves the same. The round trip would need its own
test, as for titles and profiles.

## 10. What was built (2026-11-07) and what it does not show

- **Record and gate:** `term` kind with `term`, `definition`, `aliases`, `mappings`, `note`, `source`, `modified`; G002/G003 incl. mapping entries
  (`<id>#mappings[i].<key>`), `source` is a key or `{key, iri, label}` (key a bibliography anchor, so no slash; address and label plain), `modified` needs
  `source`, an address may not contain whitespace or brackets; T001-T005 as in section 5 (T005 only with `[terms] mappings = "normative"`).
- **Emitter:** `terms.adoc`, written only when there are term records, one entry per term (heading, `alt:` lines, definition, the term's note,
  `[.source]` with `<<key>>` or `<<key, key, iri[label]>>`, and `, modified`). `mappings` is not emitted (decision D). All prose is literal text. A closing bracket or backslash in a term, alias,
  definition or note, an unusable address, or a note starting "Mapping (" is refused (exit 2) rather than emitted.
- **Document:** the project's terms clause must be marked `[heading=terms and definitions]` and `include::terms.adoc[]` (see `ogcspec-metanorma`).
  Hand-written terms beside the emitted ones are fine.
- **Stage 2:** `terms_from_xml` (kept apart from `scan_xml`, so no corpus record count changes) and `term_fidelity`: each record term is matched to an XML
  entry by designation (ignoring case and spacing); not found is X001 (`term:<id>`); a field difference is X003 (`<id>#definition`, `aliases`,
  `note`, `source`, `source.iri`, `source.label`, `modified`; the address and label are compared only when the record gives them). A term in the
  XML that the records do not define is **never** reported. `mappings` is record-only and not compared.
- **Tests:** gate 117 (3 skipped without the corpus), emitter and round trip 36, including a real compile on the pinned image of four terms (special
  characters, a modified source with an address, a key-only source, a hand-written neighbour) that come back identical, a mutated record reported as X003,
  a missing term as X001, and a control showing that a key-only citation draws no STANDOC_7.
  A real compiled document is kept as a gate fixture (`tests/fixtures/c8_terms`).
- **Corpus:** the six real documents (rebuilt earlier the same day at their pinned SHAs) were re-checked after the first version of these changes
  (116 gate tests, none skipped, counts equal the snapshot) and again after decision D (117 gate tests, none skipped, counts equal the snapshot).
- **Not shown:** a real standard's terms clause; the editions of the Directives after 9.0; whether a `[SOURCE: ...]` key that is not in the
  document's references is caught by anything but Metanorma's own warning (STANDOC_32); that any mapping is correct.

## 11. Dry run on a real terms clause (CS API Part 1, 2026-11-07; a throwaway copy, nothing committed)

Method: the 17 terms of `clause_4_terms_and_definitions.adoc` (corpus copy at the pinned SHA `8e03b236`) were turned into term records by a small
parsing script (mine, scratch only), emitted with `emit.py`, spliced into a copy of the document (the clause marked `[heading=terms and definitions]`,
its one hand-written sentence kept, the entries `include::`d), and compiled on the pinned image with `--root`.

- **It works at real size:** compile exit 0 in about 48 s; all 17 terms read back with **no** X001/X003; the same kinds of Metanorma message as the
  original (no new kind). The total fell from 243 to 193, almost all STANDOC_7 (136 to 88); most plausibly the original's source-locator links, not checked.
- **The first carrier differed from existing practice** (a note "Mapping (<relation>): <address>" plus a bare key; against the original's hand-written terms the
  gate reported X003 on `mappings` for 10 terms for that reason alone). After decision D the dry run was repeated with `source: {key, iri, label}` records:
  compile exit 0; read-back of the emitted copy had **no** findings; against the **original hand-written clause** the 10 address differences are gone and
  only three remain, all real: the Actuator entry's dangling key (below), the Property entry's `Example` paragraph and the Sensor Network entry's lowercase
  `Note:` (the last is a slip of my parsing script). Metanorma's STANDOC_7 count went from 136 (original) to 137 (re-emitted): the source-locator link form draws
  those XML-syntax messages in OGC's own document too, so a project using it baselines them.
- **Gaps in the term format shown by real terms:** no field for an `Example` (the Property entry has one); one `note` only (the directives allow several);
  a definition is one string; the source's locator text (`definition 4.11`, `definition 4.1.4`) has nowhere to go (`source` is a key only);
  the source status is identical or modified only (the 5-word relation has no counterpart in the document).
- **A defect in that real document, not ours:** the Actuator entry cites `<<SOSA/SSN, SOSA-SSN, ...>>`, i.e. key `SOSA/SSN` where the bibliography anchor is
  `SOSA-SSN`; the compiled XML has `bibitemid="SOSA/SSN"`, a dangling reference. This module's `source` check refuses a key with a slash.
- **My parsing slips, not template issues:** a lowercase `Note:` (Sensor Network) was read as part of the definition.
