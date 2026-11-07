# Requirement record format: proposal (plan step 2)

**Status: proposal, 2026-11-06. Nothing here is enforced.** `gate.py`, `emit.py` and the `SKILL.md` kind table were not
changed. The proposal says what the tools do today with each proposed field (section 7, run on the pinned image) and what
step 3 would have to change. Several points are **open** and need the owner or the ModSpec maintainers.

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

- `title` is read by the gate, which resolves an `inherit` entry given by title (OGC API - Records does this). The emitter
  does not emit it (**observed**, v2).
- Membership of a requirement in a class is the class's `requirements` list (Req 28, **read**).
- `kind` is the discriminator. The emitter refuses an unknown kind (exit 2) and the gate reports G001 (**observed**, v6).

## 2. Document-level facts stay in the gate config

`namespace`, `core`, `core_dependency`, `style`, `[verbal_forms]` and `[[normative_references]]` stay in
`ogcspec.gate.toml`. Do **not** add a document-level record kind to carry them: a new kind is refused by the emitter and
reported by the gate (**observed**, v6), so it breaks both tools until step 3 changes them. The plan's "a `namespace`" is
already satisfied by the config.

## 3. Fields this proposal adds

All optional, all additive: a record without them stays valid and means what it meant before.

| field | on | type | basis | Metanorma mapping | today (observed) |
|---|---|---|---|---|---|
| `depends_on` | `conformance_class` | list of ids, **external conformance classes only** (section 4) | Req 12 (**read**) | `inherit::` on the conformance class block; Metanorma keeps it and the gate reads it back (v5b) | ignored, not emitted (v3) |
| `uml_package` | `requirements_class` | one string, the qualified name of the UML package | Part 2 REQ004-006 define no notation (**read** via digest); this is the project's own convention (section 6) | none: record-only | ignored (v2) |
| `status` | any kind | `proposed` or `accepted` | design doc H1; no ModSpec basis | none: record-only | ignored (v1) |
| `title` | `requirements_class`, `conformance_class` | string | Req 14: classes "explicitly named", corresponding ones "similar names" (**read**) | not emitted; how Metanorma would carry it is untested (**open**) | ignored (v2); the gate reads it on requirements classes only |

Not proposed: dependencies between individual requirements. Part 1 Reqs 12, 16, 17 and 18 speak of classes; I read no
Part 1 requirement on dependencies between single requirements.

## 4. Conformance-class dependencies (Req 12)

Req 12 (**read**): a conformance class "SHALL specify any other conformance class upon which it is dependent", and that
class "SHALL be used to test the specified dependency". ATS 12 and ATS 19 are "Inspect the document" tests, so no tool can
check the second half; the gate can only check that dependencies are stated and resolve.

Today a conformance class's dependencies are not in the records at all: a YAML `inherit` on a conformance class is dropped
by the emitter and then reported as X003 (**observed**, v4), and M009/M010 read `inherit` on requirements classes only
(**read** in `gate.py`). Adding the line to the AsciiDoc by hand without the YAML also gives X003 (v5a). With both, the
round trip is clean (v5b).

Options:

- **A. Author `depends_on` for every dependency.** Matches the text of Req 12 literally, but the internal part repeats
  what the requirements class's `inherit` already says (through Req 8, one-to-one), so the two lists can disagree.
- **B. Derive internal dependencies, author external ones.** (**Recommended**, **open**.) For each `inherit` entry of
  a requirements class that is another requirements class of the document, the emitter writes the `inherit::` of the
  corresponding conformance class (Req 8). `depends_on` lists only dependencies that cannot be derived: external
  conformance classes. There is one source of truth for each fact. A step 3 rule would reject a `depends_on` entry that
  names a conformance class of this document, as redundant.
- **C. Derive external dependencies as well, by renaming `/req/` to `/conf/`.** Rejected: ModSpec does not define the
  mapping from an external requirements class to its conformance class (**read**: Req 13 says an imported requirements
  class "SHALL be a conformance class of the source standard", not how to name it). Guessing it would invent URIs.

Open: whether the owner accepts B, and whether the maintainers read Req 12 as covering a dependency that exists only
through a requirements class's `inherit`.

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
- A step 3 rule can check only what the records hold: present (opt-in, since Part 2 is an optional Part and whether it
  applies to a given standard is **open**), and unique across classes. It cannot check that the package exists or that
  package dependencies match class dependencies (REQ008-009) without a model export, which this format does not define.

## 7. Observed behaviour of the current tools

`docs/design/record-format-experiment.py` builds a baseline of two requirements/conformance class pairs, applies one change
per variant, then runs emit, a compile with the pinned image (`METANORMA-PIN`, metanorma 2.5.16, offline) and the gate with
stage 2. Run 2026-11-06. Every variant compiled (exit 0) unless noted. "Baseline Metanorma messages" are the five messages the baseline always produces (`MODSPEC_1` twice, `MODSPEC_2`,
`OGC_14`, `STANDOC_40`; the gate reports each as X010), so the gate exits 1 on all variants unless a baseline file accepts
them. The table lists other findings only.

| variant | change | emitted bytes vs baseline | findings besides the baseline messages |
|---|---|---|---|
| v0 | baseline | - | none |
| v1 | `status: proposed` on every record | identical | none |
| v2 | `uml_package` and `title` on classes | identical | none |
| v3 | `depends_on` on a conformance class | identical | none |
| v4 | `inherit` on a conformance class, YAML only | identical | `X003 /conf/ext#inherit` |
| v5a | `inherit::` added to the AsciiDoc only | differs (that file) | `X003 /conf/ext#inherit` |
| v5b | `inherit` in YAML and in the AsciiDoc | differs (that file) | none; XML carries `<inherit>/conf/core` |
| v6 | a `profile` record kind | emitter refuses (exit 2) | gate: `G001` unknown kind |
| v7 | a misspelled field (`requirments`) beside the right one | identical | none: silently ignored |
| v8 | a test of another class's requirement listed by a conformance class | differs | `M006` (YAML and XML) |
| v9 | one record per file instead of one list | identical | none |
| v10 | the same id in two files | differs | `M001`; the compile fails (exit 1) and the gate adds `X000`; Metanorma adds `STANDOC_36` and `MODSPEC_3` |
| v11 | the worked example, `record-format-example.yaml` | - | none |

What this shows. The proposed record-only fields cost nothing today and do nothing today. The one place a new field
would change output is the conformance-class `inherit`, and there the emitter and gate must change together (v4, v5a, v5b).
Not tested: the Metanorma representation of `title` or of a profile; any ModSpec rule beyond what the gate already has.

## 8. `status: proposed | accepted` (needs the owner's decision)

`docs/design/personas-and-workflow.md` lists this as open, tied to H1 (a person mints and approves identifiers).

- Agents write only `proposed`. Moving a record to `accepted` is a human act, made in a commit authored by that person.
- A record without `status` stays valid and means "no workflow state recorded". The module's agents would treat it as `proposed`.
- It is record-only: not emitted (the published document must not carry draft markers) and ignored by the tools today (v1).
- It is a marker, **not a control**: an agent with write access can edit the field. Mechanical enforcement needs a control
  outside the record, such as the "approved identifiers" file or code-owner review that the design doc sketches. **Open**
  (owner), as is whether one field per record is enough when identifiers (H1) and normative wording (H2) are approved separately.

## 9. Profiles (Req 19): not designed

Req 19 (**read**): conformance tests for a profile "SHALL be defined as the union of a list of conformance classes". A
`profile` kind would need both tools to change (v6), and how Metanorma would represent it is untested. A profile may also
be expressible as a conformance class that depends on the constituent ones, but I did not test that. Deferred: a template
for new standards need not support profiles at first. **Open.**

## 10. Layout: one record per file (convention)

Recommended, not required (**open**): one record per file, with the path following the id, for example `records/req/core.yaml`
for `/req/core` and `records/req/core/first.yaml` for `/req/core/first`. Reasons (**inferred**): a review diff is one record,
ownership can follow the path, and a duplicate id is a visible collision. Observed (with numbered file names, not the path rule): splitting records into one file each changes nothing in the
emitted text (v9, byte-identical to a single list file), and a duplicate id across files is caught (v10). Against: a large standard
has hundreds of files, and identifiers are not restricted to filename-safe characters. If adopted, enforcement would be an
opt-in style rule (`S`), because no ModSpec or Policy text asks for it.

## 11. Unknown fields: a prerequisite for the rest

A misspelled or unsupported field is silently ignored today (v7). With only the fields in section 1 that is a nuisance; with
record-only fields it becomes ambiguous, because a typo and a deliberate record-only field look the same. Step 3 should add
a rule that reports any field outside a per-kind table (a new `G` rule, not an OGC-derived one), before or together with the
fields in section 3. Whether project-private fields get a reserved prefix is **open**.

## 12. What step 3 would change if this is accepted

1. Gate: a known-field table per kind and a rule for unknown fields (section 11); `depends_on` resolution and the
   redundancy rule (section 4); optional rules for `uml_package` (section 6) and `status`/layout (sections 8, 10).
2. Emitter: write `inherit::` on conformance classes from the derived and authored dependencies; stage 2 then compares it.
3. Fixtures: the variants in section 7 as test cases, with `record-format-example.yaml` as the clean case.
4. Nothing for Req 5 (section 5); nothing for Req 19 until section 9 is decided.

## Open decisions, in one place

| # | question | who |
|---|---|---|
| 1 | Accept option B for conformance-class dependencies? | owner |
| 2 | Does Req 12 cover a dependency that exists only through a requirements class's `inherit`? | ModSpec maintainers (add to the question list) |
| 3 | Is `uml_package` wanted, and when is Part 2 "relevant" so the rule is on? | owner; maintainers (existing question 3) |
| 4 | Adopt `status`, and by what control are `accepted` records protected? | owner |
| 5 | Should `title` be emitted, and how does Metanorma carry it? | owner; needs a compile test |
| 6 | Profiles: in the template at all? | owner |
| 7 | One record per file, and the path rule? | owner |
| 8 | Reserved prefix for project-private fields? | owner |
