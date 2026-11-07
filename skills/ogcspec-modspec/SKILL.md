---
name: ogcspec-modspec
description: Draft and revise OGC ModSpec requirement records (requirements, classes, abstract tests, conformance classes) as YAML. Use when asked to write or change normative requirements for the standard.
---

# Drafting requirement records

The YAML records under the standard's `records_dir` are the source of truth. The Metanorma AsciiDoc is
generated from them (`ogcspec-metanorma`) and is never edited by hand.

## Record kinds (what `ogcspec-gate` reads)

| kind | id pattern | fields |
|---|---|---|
| `requirements_class` | `/req/<class>` (shape is a habit, see below) | `subject` (one string), `inherit[]`, `requirements[]`; optional `title`, `uml_package`, `profile` |
| `requirement` | `/req/<class>/<name>` | `statement` |
| `abstract_test` | `/conf/<class>/<name>` | `target` (a requirement id), `purpose`, optional `steps[]` |
| `conformance_class` | `/conf/<class>` | `target` (a requirements class id), `tests[]`; optional `title`, `depends_on[]` |
| `recommendation` | `/rec/<class>/<name>` | `statement` (never needs a test) |
| `permission` | `/per/<class>/<name>` | `statement` (never needs a test) |

Any kind may carry `status: proposed` or `accepted`. Any other field is G002. The fields are explained, with their ModSpec
basis and what each rule checks, in `references/record-format-proposal.md`; `references/record-format-example.yaml` uses all of
them. In short:

- `title`: the class's name in the document. `uml_package`: the UML package of a requirements class (record-only, the
  project's own convention). `status`: record-only workflow marker.
- `depends_on`: conformance classes **outside** this document that a conformance class depends on (Req 12). Dependencies on
  other classes of this document are derived from the requirements class's `inherit`; writing one is G004.
- A **profile** (Req 19) is a requirements class with `profile: true`, no `requirements` and the classes it builds on in
  `inherit`, plus its conformance class with no `tests`. Metanorma warns that both are empty (`MODSPEC_1`); that is expected and
  goes in the baseline.
- Recommended layout: one record per file, path = id without the leading `/` plus `.yaml` (`style = ["layout"]` checks it).

A file holds one mapping or a list of them. Membership of a requirement in a class is the class's `requirements`
list (ModSpec Req 28); the identifier shape above is a convention that `style = ["prefix"]` can check, not an OGC rule.
Identifiers may be relative (`/req/core`) or absolute under the document's `namespace` (set in the gate config).

## How to work

1. Draft only what was asked. Do not add requirements the user did not describe.
2. Every `requirement` needs an `abstract_test` that targets it, listed by exactly one `conformance_class`;
   every requirement is listed by its `requirements_class`. Write the test `steps` only from what the
   requirement text says. If a requirement cannot be turned into a step without guessing, say so and stop
   rather than inventing a step. A step that merely restates its requirement (no input, no pass/fail rule) leaves the
   test unrepeatable: after drafting, list what the requirement does not decide (what counts as the thing, how many, what
   fails, the empty or partial case, undefined terms) as open questions for the owner, and do not settle them yourself.
   The owner's answer changes the requirement first and the steps second. (Review run 2026-11-07: every lens flagged this.)
3. Write `status: proposed` on every record you draft; never write `accepted`, which is a person's act. Identifiers you write are proposals. A person mints and approves identifiers and any `opengis.net`
   URI; never present one as assigned.
4. External `inherit` targets must match a `[[normative_references]]` `uri_prefix` in the gate config. Add
   the reference to the config only when the user has named the dependency.
5. After editing, run `ogcspec-gate` and report its findings as they are. Never edit the baseline file to
   make a finding disappear; that is a human decision.

## Limits to state when relevant

- Verbal forms: the ModSpec Policy (OGC 25-001, a DRAFT) points to ISO/IEC Directives Part 2 clause 7. The gate
  (P002/P003) applies that clause as read from edition 9.0 (2021-05, a redline copy): `shall` / `shall not` for
  requirements, `should` / `should not` for recommendations, `may` for permissions, and no `must` or `may not` in a
  provision (`must` is reserved for external constraints). The clause says nothing about case, so matching ignores
  case; OGC documents use both `SHALL` and `shall`. Whether a newer edition changed clause 7 has not been checked.
  A project can override the forms in `[verbal_forms]` or switch the rules off with `iso_verbal_forms = false`.
- The gate's M rules are ModSpec Part 1 requirements, each cited by number in `gate.py`. Some have two readings
  (Req 22 "direct" dependency; Req 27/28 against documents that list another class's requirement). The gate
  implements the literal reading and says so; a finding under one of them may be a disagreement about the text.
- `references/identifier-convention.md` records what ModSpec requires and what real documents do.
