# Requirement record format (plan steps 2 and 3)

**Status: decided by the owner on 2026-11-06 and implemented in plan step 3.** Written first as a proposal (commit `d304d5c`);
the gate (`c885300`) and the emitter (`a6e69d7`) now implement it. Sections 7 and 13 give what the tools did *before*
(commit `b401284`, observed) and what they do now. The sections are still worded as the proposal was; where they say "step 3
would", step 3 has done it, and section 12 lists what.

Markers: **read** (from a source opened for this work), **observed** (produced by running the pinned tools, section 7),
**inferred** (my reasoning), **open** (undecided). ModSpec Part 1 means OGC 08-131r7, read from the local copy of its
sources (`requirements/core/REQ*.adoc`, `abstract_tests/core/ATS*.adoc`) on 2026-11-06. Part 2 statements come from
`docs/research/modspec-parts-2-3-digest.md`, not re-read here. All identifiers in examples are placeholders; none is
assigned or proposed for a real standard. The shape `/req/<class>/<name>` is a habit, not a ModSpec rule (see
`identifier-convention.md`).

## 1. Baseline: the current format, unchanged

One YAML mapping per record; a file holds one mapping or a list. These are the fields the gate reads and the emitter
writes today (`gate.py` header, `emit.py` `emit_record`).

| kind | fields | emitted as (Metanorma `[%metadata]` keys) |
|---|---|---|
| `requirements_class` | `id`, `subject` (one string), `inherit[]`, `requirements[]`; `title` optional | `identifier`, `subject`, `inherit` (one per entry), `requirement` (one per entry) |
| `requirement`, `recommendation`, `permission` | `id`, `statement` | `identifier`, `part` (literal text) |
| `abstract_test` | `id`, `target` (a requirement id), `purpose`, `steps[]` optional | `identifier`, `target`, `test-purpose`, `test-method` with `step` entries |
| `conformance_class` | `id`, `target` (a requirements class id), `tests[]` | `identifier`, `target`, `conformance-test` (one per entry) |

- `title` is read by the gate, which resolves an `inherit` entry given by title (OGC API - Records does this). Before step 3 the
  emitter did not emit it (**observed**, v2); now it does (section 13).
- Membership of a requirement in a class is the class's `requirements` list (Req 28, **read**).
- `kind` is the discriminator. The emitter refuses an unknown kind (exit 2) and the gate reports G001 (**observed**, v6).

## 2. Document-level facts stay in the gate config

`namespace`, `core`, `core_dependency`, `style`, `[verbal_forms]` and `[[normative_references]]` stay in
`ogcspec.gate.toml`. Do **not** add a document-level record kind to carry them: a new kind is refused by the emitter and
reported by the gate (**observed**, v6), so it breaks both tools until step 3 changes them. The plan's "a `namespace`" is
already satisfied by the config.

## 3. Fields this proposal adds

All optional, all additive: a record without them stays valid and means what it meant before. Any field outside the table
for its kind is G002.

| field | on | type | basis | Metanorma mapping | before step 3 (b401284, observed) | now |
|---|---|---|---|---|---|---|
| `depends_on` | `conformance_class` | list of ids, **external conformance classes only** (section 4) | Req 12 (**read**) | `inherit::` on the conformance class block, after the derived entries; Metanorma keeps it (v5b) | ignored, not emitted (v3) | emitted; G003 wrong type, G004 names a class of this document, M014 unresolved |
| `uml_package` | `requirements_class` | one string, the qualified name of the UML package | Part 2 REQ004-006 define no notation (**read** via digest); this is the project's own convention (section 6) | none: record-only | ignored (v2) | not emitted; G003; opt-in S003, S004 |
| `status` | any kind | `proposed` or `accepted` | design doc H1; no ModSpec basis | none: record-only | ignored (v1) | not emitted; G003 for any other value |
| `title` | `requirements_class`, `conformance_class` | non-empty string | Req 14: classes "explicitly named", corresponding ones "similar names" (**read**) | block title `.pass:c[...]`; compiles to the XML `<title>` (section 13) | not emitted (v2); the gate read it on requirements classes only | emitted; compared in X003 for both kinds; G003 |
| `profile` | `requirements_class` | `true` or `false` | this project's design for Req 19 (section 9), not in the owner's list | none: record-only | unknown field | not emitted; M013 |

Not proposed: dependencies between individual requirements. Part 1 Reqs 12, 16, 17 and 18 speak of classes; I read no
Part 1 requirement on dependencies between single requirements.

## 4. Conformance-class dependencies (Req 12)

Req 12 (**read**): a conformance class "SHALL specify any other conformance class upon which it is dependent", and that
class "SHALL be used to test the specified dependency". ATS 12 and ATS 19 are "Inspect the document" tests, so no tool can
check the second half; the gate can only check that dependencies are stated and resolve.

Before step 3 a conformance class's dependencies were not in the records at all: a YAML `inherit` on a conformance class was
dropped by the emitter and then reported as X003 (**observed**, v4), and M009/M010 read `inherit` on requirements classes
only (**read** in `gate.py`). Adding the line to the AsciiDoc by hand without the YAML also gave X003 (v5a). With both, the
round trip was clean (v5b).

**Implemented.** `conformance_inherit` (in `gate.py`, with an identical copy in `emit.py` and a test that keeps them equal)
derives each conformance class's dependency list; the emitter writes it as `inherit::` lines and stage 2 compares it with
the compiled document (X003), so any drift between the two derivations shows up as a build failure. The rules about it run
on authored records only: they never run on a document rebuilt from compiled XML, because a completeness rule for Req 12
would encode the contested reading (maintainer question 6) and fire on approved OGC documents. Only `depends_on` is
checked: G004 (repeats a dependency already derived from `inherit`; changed 2026-11-09, see below) and M014 (a relative id that is no class here, or an external id matching no
declared normative reference, when references are declared).

**Changed 2026-11-09 (owner decision, after a trial needed it).** G004 originally fired on any `depends_on` entry naming a class of this document. That made an **indirect dependency** inside the document impossible
to write: ModSpec 6.1.5 defines it as a dependency on a class with a different standardization target, and Req 12 says the dependency may be "in the same standard"; such a class cannot be derived from `inherit` (and must not be
listed there, since `inherit` of the same target is a direct dependency, 6.1.3). Now G004 fires only when the entry repeats a dependency already derived from `inherit`; an entry for a class of this document that `inherit`
cannot give is allowed (M014 still checks that it exists, and that it is not the class itself). The emitter already writes derived entries and then authored ones. Whether ModSpec intends the requirements class to list it too is
maintainer question 8; the format changes again if they answer differently.

Options:

- **A. Author `depends_on` for every dependency.** Matches the text of Req 12 literally, but the internal part repeats
  what the requirements class's `inherit` already says (through Req 8, one-to-one), so the two lists can disagree.
- **B. Derive internal dependencies, author external ones.** (**Chosen by the owner, 2026-11-06.**) For each `inherit` entry of
  a requirements class that is another requirements class of the document, the emitter writes the `inherit::` of the
  corresponding conformance class (Req 8). `depends_on` lists only dependencies that cannot be derived: external
  conformance classes. There is one source of truth for each fact. A step 3 rule would reject a `depends_on` entry that
  names a conformance class of this document, as redundant.
- **C. Derive external dependencies as well, by renaming `/req/` to `/conf/`.** Rejected: ModSpec does not define the
  mapping from an external requirements class to its conformance class (**read**: Req 13 says an imported requirements
  class "SHALL be a conformance class of the source standard", not how to name it). Guessing it would invent URIs.

Still open, for the ModSpec maintainers: whether Req 12 covers a dependency that exists only through a requirements
class's `inherit`.

## 5. Test target type (Req 5): no field

Req 5 (**read**): all conformance tests in one conformance class "SHALL have the same standardization target type".
Plan step 3 said this "needs a target-type field on tests". It does not, **inferred** from the existing rules:

- a requirements class names one target type, its `subject` (Req 4, rule M004);
- a conformance class corresponds to one requirements class and tests all and only its requirements (Reqs 8, 11, 15; M005, M006);
- so every test of a conformance class tests a requirement of one class, and has that class's `subject`.

A per-test field would add a second place for the same fact. It would catch a test that tests a requirement of a different
class, but M006 already reports that (**observed**, v8). A listed test whose requirement belongs to a different class is exactly
what M006 rejects, so the two values cannot differ in a document that passes the gate. What neither catches: two `subject` strings that mean the same target type, or one string covering two. Those are human judgements;
`subject` is compared as text.

Step 3 should therefore add no Req 5 rule; M004-M006 already imply it. **Open** only if the owner wants Req 5 reported by
number.

## 6. UML package mapping (project convention, not ModSpec)

Part 2 says each requirements class is "associated to a unique package" and to "some number of complete leaf packages"
(REQ004-006), and defines no notation, tag, stereotype or record field for the association (**read** via digest, its item
14). The proposal puts one string on the requirements class:

```yaml
uml_package: example::core     # qualified name in the standard's own UML model; syntax is the project's
```

- It is one string because REQ005 says "a unique package"; leaf packages below it belong to the class by containment.
- It is record-only: not emitted, not compared in stage 2 (**observed**, v2). It documents the mapping; it does not put it in
  the Metanorma document.
- The rules check only what the records hold, and only with `style = ["uml"]` (Part 2 is an optional Part and whether it
  applies to a given standard is **open**): S003 every requirements class names a package, S004 no two share one. They cannot
  check that the package exists or that package dependencies match class dependencies (REQ008-009) without a model export,
  which this format does not define.

## 7. Observed behaviour: the tools before step 3, and after

`docs/design/record-format-experiment.py` builds a baseline of two requirements/conformance class pairs, applies one change
per variant, then runs emit, a compile with the pinned image (`METANORMA-PIN`, metanorma 2.5.16, offline) and the gate with
stage 2. Run 2026-11-06, first against the tools at commit `b401284` (the "before" column, which is what the proposal was
written from), then against the implementation (the "after" column). Every variant compiled (exit 0) unless noted. "Baseline Metanorma messages" are the five messages the baseline always produces (`MODSPEC_1` twice, `MODSPEC_2`,
`OGC_14`, `STANDOC_40`; the gate reports each as X010), so the gate exits 1 on all variants unless a baseline file accepts
them. The table lists other findings only.

| variant | change | before: findings besides the baseline messages | after step 3 |
|---|---|---|---|
| v0 | baseline | none | none |
| v1 | `status: proposed` on every record | none; emitted bytes identical | none |
| v2 | `uml_package` and `title` on classes | none; bytes identical (title not emitted) | none; the title is emitted and X003 compares it |
| v3 | `depends_on` naming `/conf/core` on `/conf/ext` | none; ignored | `G004` (it is derived from `/req/ext`'s `inherit`) |
| v4 | `inherit` on a conformance class, YAML only | `X003 /conf/ext#inherit` | `G002`, with a message pointing to `depends_on` |
| v5a | `inherit::` added to the AsciiDoc only | `X003 /conf/ext#inherit` | `X003`: the patch duplicates the line the emitter now writes, and the duplicate is caught |
| v5b | `inherit` in YAML and in the AsciiDoc | none; XML carried `<inherit>/conf/core` | `G002` and `X003` (same duplicate); obsolete as a test of the emitter |
| v6 | a `profile` record kind | emitter refuses (exit 2); gate `G001` | unchanged |
| v7 | a misspelled field (`requirments`) beside the right one | none: silently ignored | `G002`, "did you mean 'requirements'?" |
| v8 | a test of another class's requirement listed by a conformance class | `M006` (YAML and XML) | unchanged |
| v9 | one record per file instead of one list | none; bytes identical | none; bytes identical |
| v10 | the same id in two files | `M001`; compile fails (exit 1), gate adds `X000`; Metanorma adds `STANDOC_36`, `MODSPEC_3` | unchanged |
| v11 | the worked example, `record-format-example.yaml` | none (the earlier version of the file, without a profile) | none (with the profile pair; `S003`/`S004` also clean, checked separately) |

The first run of the script had `core = "/req/core"` appended after the `[[normative_references]]` table, where TOML makes it
a key of that table, so M011/M012 did not run. The config was corrected and the "before" runs repeated against `b401284`;
every result above is unchanged.

What this shows. Before step 3 the added fields cost nothing and did nothing, and a conformance-class `inherit` needed
emitter and gate to change together; they now do. Not tested: any ModSpec rule beyond what the gate already has; the
corpus of approved OGC documents (see the status of the corpus test in `docs/HANDOFF.md`).

## 8. `status`: proposed or accepted

`docs/design/personas-and-workflow.md` lists this as open, tied to H1 (a person mints and approves identifiers).

- Agents write only `proposed`; the ModSpec Architect's instructions say so. Moving a record to `accepted` is a human act, made in a commit authored by that person.
- A record without `status` stays valid and means "no workflow state recorded". The agents treat it as `proposed`.
- It is record-only: not emitted (the published document must not carry draft markers). The gate checks only that the value is one of the two (G003).
- It is a marker, **not a control**: an agent with write access can edit the field. Mechanical enforcement needs a control
  outside the record. **Decided (owner, 2026-11-07): branch protection in the target standard's repository, no gate rule.** Put
  the records directory under `CODEOWNERS` (for example `/records/ @<the-people-who-approve>`) and turn on "Require review from
  Code Owners" for the default branch, so nothing reaches it without a named person's review. This is coarse: it guards the
  directory, not the `status` field, so a reviewer must read the diff for a changed `status`. The template cannot configure a
  repository's settings and this repository holds no records, so nothing is set here. **Open:** whether one field per record is
  enough when identifiers (H1) and normative wording (H2) are approved separately.

## 9. Profiles (Req 19)

Req 19 (**read**): conformance tests for a profile "SHALL be defined as the union of a list of conformance classes". ModSpec's
own definition (`profile`, **read**): "a set of requirements classes or conformance classes (either preexisting or locally
defined) of the base standards". A new record kind would break both tools (v6), so the design uses the existing kinds:

- A profile is a **requirements class** that lists no requirements and has the classes it builds on in `inherit`, marked
  `profile: true`, and its **conformance class** with no tests. Its conformance class's dependencies are derived (section 4),
  so the union of the constituent conformance classes is stated in the document without being written twice. External
  constituents go in `depends_on`.
- **Observed** (section 13): this compiles on the pinned image; the XML carries the empty class and the derived `inherit` list.
  Metanorma adds two severity-2 messages of its own, `MODSPEC_1` on `/req/prof` ("has no corresponding Requirement") and on
  `/conf/prof` ("has no corresponding Conformance test"). They are expected and are accepted only through the baseline. `record-format-example.baseline.json` is that baseline for the worked example, written with `--write-baseline`
  from a real run on the pinned image (two runs gave identical bytes; the keys carry no line numbers, paths or timestamps). A test
  (`WorkedExampleBaseline`) checks that the example plus this file exits 0 and that it exits 1 without it. The gate does not
  suppress `MODSPEC_1` for profiles: a finding is accepted only through an explicit baseline, a human decision.
- `profile: true` is this project's design choice, not in the owner's list of decisions; it exists so the gate can tell a
  deliberate profile from an unfinished class. M013 checks that a profile (a) lists no requirements, (b) has a conformance
  class with no tests, (c) builds on at least one class. (b) is the reading of Req 19; (a) is **inferred**, because a
  requirement without a test breaks M007 (Req 1), so a profile with no tests of its own can have no requirements of its own.
  ATS 19 is "inspect the document": the gate checks structure only.
- **Observed** (unit test): a profile that builds only on a non-core class (not on the core) is reported by M012 as reaching the
  core only transitively, and passes with `core_dependency = "transitive"`. That is the Req 22 question (maintainer question 1)
  again, not a profile problem.
- A profile may in principle also fix options and parameters (the definition says so); this design covers only the union Req 19
  asks for.

## 10. Layout: one record per file (convention)

Chosen 2026-11-06, with the check opt-in (`style = ["layout"]`, rule S005: the file path must be the id without its leading `/`
plus `.yaml` or `.yml`, and a file holds one record): one record per file, with the path following the id, for example `records/req/core.yaml`
for `/req/core` and `records/req/core/first.yaml` for `/req/core/first`. Reasons (**inferred**): a review diff is one record,
ownership can follow the path, and a duplicate id is a visible collision. Observed (with numbered file names, not the path rule): splitting records into one file each changes nothing in the
emitted text (v9, byte-identical to a single list file), and a duplicate id across files is caught (v10). Against: a large standard
has hundreds of files, and identifiers are not restricted to filename-safe characters. If adopted, enforcement would be an
opt-in style rule (`S`), because no ModSpec or Policy text asks for it.

## 11. Unknown fields: a prerequisite for the rest

A misspelled or unsupported field was silently ignored before step 3 (v7). With only the fields in section 1 that is a nuisance; with
record-only fields it becomes ambiguous, because a typo and a deliberate record-only field look the same. G002 now reports any
field outside the per-kind table (not an OGC-derived rule), with a near-miss suggestion; G003 checks types and values. Decided
2026-11-06: no reserved prefix for project-private fields. Keys starting with `_` are the loader's own and are skipped.

## 12. What step 3 changed

1. Gate (`c885300`): G002/G003 (known fields and values), G004 and M014 (`depends_on`), M013 (profiles), S003/S004 (`uml`), S005
   (`layout`); `conformance_inherit`; X003 now compares the derived `inherit` and `title`; the conformance-class title is read from
   the XML. The new rules run on authored YAML only (`check(..., authored=True)`).
2. Emitter (`a6e69d7`): block titles as literal text, `inherit::` on conformance classes, `--config` for the namespace.
3. Tests: gate 96 run (3 skipped: the corpus tests), emitter 24 run including two Docker round trips; the worked example is the
   clean case; the variants in section 7 are in `docs/design/record-format-experiment.py`.
4. Nothing for Req 5 (section 5).

**Corpus (partly verified, 2026-11-07).** `records_from_xml` and the rule table changed, which the corpus of real OGC documents
exercises. I rebuilt four of its six documents from local clones at their pinned commits (copies; compiled offline on the pinned
image, exit 0): ModSpec 08-131r7, Connected Systems Part 1 and Part 2 at v1.0, and the Part 3 draft. Record and rule counts equal
the snapshot taken before these changes in every case (70, 244, 284 and 31 records), as does the agreement with Metanorma's own
`MODSPEC_1` messages. **Not rebuilt:** Processes and Records (no local clone; they would be fetched from GitHub) and Features
(the compile-fails case). The corpus unit test itself still skips here, because it needs all six.

## Decisions (owner, 2026-11-06)

| # | question | decision |
|---|---|---|
| 1 | Conformance-class dependencies | Option B: derive dependencies inside the standard from `inherit`, author external ones in `depends_on`. |
| 2 | Does Req 12 cover a dependency that exists only through a requirements class's `inherit`? | Not the owner's to decide: added to the questions for the ModSpec maintainers (PLAN, question 6). |
| 3 | `uml_package` | Add as an optional field; its rules are opt-in. |
| 4 | `status` (proposed or accepted) | Add the label. Protecting `accepted` records against an agent that can edit them: branch protection with code-owner review in the target repository (section 8); no gate rule. |
| 5 | `title` | Emit it in the document, after a test compile shows how Metanorma carries it. |
| 6 | Profiles | Design them in step 3, after a test compile. |
| 7 | One record per file | Yes, path follows the id; the check is opt-in. |
| 8 | Unknown fields | Report them. No reserved prefix for private fields. |

## 13. Compile tests that settled titles and profiles (before implementation, tools at `b401284`)

`docs/design/step3-compile-tests.py`, pinned image, offline, 2026-11-06. The emitted AsciiDoc was patched by hand to show what an
emitter would write.

| variant | what was written | observed |
|---|---|---|
| t1 | `.Core` block title between the style line and `====` | compiles; XML `<title>Core</title>` on the requirements class and on the conformance class; no new messages |
| t2 | the same with markup in the title: `.Core *bold* _under_ {name} -- 'q' <<x>>` | compiles, but the markup is applied (bold and the cross-reference are lost) and Metanorma reports `STANDOC_38` and eight `STANDOC_7` XML-validation messages |
| t3 | `.pass:c[Core *bold* _under_ {name} -- 'q' <<x>>]` | text kept literal; only the usual typography changes (`--` to an em dash, quotes curled), which the gate's `canon` normalises; no new messages |
| p1 | a profile from existing kinds (section 9) | compiles; XML shows `/req/prof` with `inherit` of both classes and no requirements, `/conf/prof` with `inherit` of both conformance classes and no tests; two new messages, `MODSPEC_1` on each; no gate finding |

So titles are emitted through the same literal form as prose. The round trip in `test_emit.py` (`Step3RoundTrip`) now covers a title
with markup, a derived and an external dependency, `status`, `uml_package` and a profile pair on the implementation: no X000-X003
finding, no G/M/P/S finding, the two expected `MODSPEC_1` messages, and no `STANDOC_7` or `STANDOC_38`.
