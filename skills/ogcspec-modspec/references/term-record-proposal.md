# A `term` record kind: proposal (not implemented)

**Status: proposal for the owner, 2026-11-07.** The owner chose option A ("add a `term` record kind") on 2026-11-07. This file is the
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
| `mappings` | list of mapping entries | no | links to external ontology terms (section 3) | `ontology-grounding.md`, "what a target must supply" |
| `note` | string | no | free text; where the mapping is unresolved (for example software or virtual systems) say so here | **inferred** |
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
| T001 | two terms share a `term` or alias (case-insensitive) | cheap, no false-positive risk |
| T002 | a mapping `ontology` key is not declared in `[[ontologies]]` | mirrors the `inherit` prefix rule |
| T003 | a mapping `iri` does not start with its ontology's `iri_prefix` | catches typos and wrong-ontology IRIs only; says nothing about meaning |
| T004 | `relation` outside the five words | same shape as G003 |
| T005 (opt-in, off by default) | a defined term never appears in any `statement` | substring match, **inferred** to give false hits on plurals and inflections; informational only |
| T006 (opt-in, off by default) | a capitalised term that has a record appears in prose undefined | not proposed: needs a definition of "use" the owner has not given |

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
