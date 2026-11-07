# ModSpec Requirement 22: does a transitive dependency on the core satisfy "direct dependency"?

Date of research: 2026-11-06. All local material was read only; nothing downloaded was executed or built. Scripts I wrote are in a session scratchpad directory (path omitted; the scripts are not kept) and were run with `python3 -I` from `/tmp`.

GitHub logins are given as they appear; I do not assert real names. Convention in this report: **[SOURCE]** = what a document says (quoted or counted). **[INFERENCE]** = my reasoning from sources. Where a source could not be reached, it is listed in section 7.

Abbreviations: `MS` = `docs/references/git/opengeospatial-ogc-modspec/sources/` (git clone, HEAD 726e647, 2026-09-21). `r7html` = `https://docs.ogc.org/pol/08-131r7/08-131r7.html` (front matter: "Document stage: Approved", Approval Date 2026-03-05, Publication Date 2026-05-21). `r3` = `https://docs.ogc.org/pol/08-131r3/08-131r3.pdf`, text extracted by me to `.../scratchpad/req22/r3-fresh.txt` (line numbers below refer to that file; PDF page 33 = printed page 19).

---

## 0. Short answer

- **Verdict: the text leans literal, but the question is genuinely ambiguous.** Req 22 part B says "direct dependency", and the two community statements I found (ogcapi-features #123, ogcapi-coverages #181) read "direct" as "listed". Against that, ModSpec's own definition of "direct dependency" can be read as satisfied by a chain (section 6.1). I would not call either reading settled.
- **[SOURCE]** No ModSpec text says a transitive dependency satisfies Req 22, and none says it does not. ATS 22 is "Inspect the document to verify the above" with no further criterion. No issue, PR or commit in `opengeospatial/ogc-modspec` discusses it.
- **[SOURCE, counted]** In 12 approved OGC documents with an identifiable core/base class (160 non-core classes), only OGC API - Features Part 1 has every non-core class list the core itself. Overall: 76 classes list the core directly, 28 reach it only through other classes, 36 do not reach it at all, 19 reach it only through "Indirect prerequisite" links to a different target type, 1 lists it only as a "Conditional Dependency". The literal reading would flag 84.
- **Only the ModSpec maintainers/OGC can settle** whether the core must appear in each class's own dependency list. A precise question is in 6.4.

---

## 1. Exact text of Req 22 and ATS 22

### 1.1 r7 (OGC 08-131r7, ModSpec Part 1 v1.1)

Source file `MS/requirements/core/REQ22_req-class-not-core-stt-subtype-of-core.adoc`, lines 7-9:

```
identifier:: /req/core/req-class-not-core-stt-subtype-of-core
part:: Every requirements class in the standard, with the exception of the core, _SHALL_ have a standardization target type which is a subtype of that of the core.
part:: Every requirement class in the standard, with the exception of the core, _SHALL_ have the core as a direct dependency.
```

The published HTML renders the same (r7html line 2693-2694; text: "Requirement 22 Identifier /req/core/req-class-not-core-stt-subtype-of-core Included in Requirements class 1: https://www.opengis.net/spec/modspec-1/1.1/req/req-class-core A Every requirements class in the standard, with the exception of the core, SHALL have a standardization target type which is a subtype of that of the core. B Every requirement class in the standard, with the exception of the core, SHALL have the core as a direct dependency.").

Introductory sentence in the same section (`MS/sections/06-req-class.adoc` line 351): "The following states that all non-core requirements classes have a standardization target type that is a sub-type of the core." It mentions only part A. The sentence was added by `cnreediii` in commit 59a35b5a (2025-03-12, "Change URI for req 22 and add informative intro to req 22").

### 1.2 ATS 22 in r7

`MS/abstract_tests/core/ATS22_req-class-not-core-stt-subtype-of-core.adoc`, lines 5-8 (identical in r7html line 2927):

```
identifier:: /conf/core/req-class-not-core-stt-subtype-of-core
target:: /req/core/req-class-not-core-stt-subtype-of-core
test-purpose:: Validate that every requirements class in the standard, with the exception of the core, has a standardization target type which is a subtype of that of the core. And that every requirement class, with the exception of the core, has the core as a direct dependency.
test-method:: Inspect the document to verify the above.
```

**What ATS 22 tests [SOURCE]:** two things, by manual inspection: (a) each non-core class has an STT that is a subtype of the core's STT; (b) each non-core class "has the core as a direct dependency". It gives no procedure, no definition of how to decide "direct", and no mention of transitive or indirect dependencies. It restates the requirement.

### 1.3 r3 (OGC 08-131r3, 2009)

Requirement text, r3-fresh.txt lines 1226-1229 (PDF page 33, clause 6.5.4):

> "Req 22 Every other requirements class in a specification shall have a standardization target type which is a subtype of that of the core and shall have the core as a direct dependency."

It is the same rule in one sentence. Differences from r7: "Every other requirements class in a specification" became "Every requirements class in the standard, with the exception of the core"; the single sentence became two parts. "direct dependency" is unchanged. The 2025 edit history of the r7 file shows only editorial changes: 8654a209 (2025-03-12, typo "hich" and URI rename), bde9ec91 (2025-03-14, "Slight wordsmithing"), b8955012 (2025-08-23, "Issue 88", "a standard" to "the standard"). All via `gh api repos/opengeospatial/ogc-modspec/commits?path=...`.

The r3 abstract test appears twice with identical text under two different headings (r3-fresh.txt lines ~1756-1770, PDF page 48): "A.1.21 General conditions are in the core" and "A.1.22 Every extension has a consistent target type". Both read: "Every other requirements class in a specification shall have a standardization target type which is a subtype of that of the core and shall have the core as a direct dependency. a) Test Purpose: Verify that this requirement is satisfied. b) Test Method: Inspect the document to verify the above." Again no criterion.

---

## 2. ModSpec definitions

### 2.1 Part 1 (r7) definitions

`MS/sections/04-terms-and-defs.adoc` (r7html clause 6.1; the same text is in `MS/sections/definitions.adoc` lines 98-123, the Annex C data-dictionary copy):

- Line 21-23, **dependency**: "module (the target) which is used by, produced by, or associated with an implementation of the source module".
- Lines 26-32, **direct dependency**: "another requirements class (the dependency) whose requirements are defined to also be requirements of this requirements class". NOTE 1: "A direct dependency (of a requirements class) of the current requirements class will have the same standardization target as the current requirements class. This is another ways of saying that the current requirements class extends, or uses all the aspects of the direct dependency (or a requirements class). Any tests associated with this dependency can be applied to this requirements class." NOTE 2: "When testing a direct dependency of a requirements class, the standardization target is directly subject to the test in the specified conformance test class of the direct dependency of a requirements class."
- Line 37, **extension**: "requirements class which has a direct dependency on another requirements class".
- Lines 43-48, **indirect dependency**: "requirements class with a different standardization target which is used by, produced by, or associated with the implementation of this requirements class". NOTE: "... Direct dependencies test the same standardization target, but indirect dependencies test related but different standardization targets. For example, if a DRM-enabled service is required to have an association to a licensing service, then the requirements of a licensing service are indirect requirements for the DRM-enabled service."
- Line 13 of `definitions.adoc` / line 18 of `04-terms-and-defs.adoc`, **building block (foundation)**: "requirements class or requirements package with no direct dependencies on other requirements classes or packages and their associated conformance test class or conformance test package".
- **requirements class dependency**: no separate term exists. The UML model gives the attribute (`MS/models/ogc-modspec.lutaml` lines 105-110): "dependencies: RequirementsClass[0..*] { definition { Requirements classes that this requirements class depends on. These dependent requirements classes must be satisfied for this requirements class to be satisfied. } }". The ConformanceClass description (lines 66-69) says: "If class "a" is dependent on class "b", then to pass the test for "a" a standardization target must also pass the test for "b."" The model has one `dependencies` attribute with no direct/indirect distinction and no statement on transitivity.
- r3 has the same direct/indirect definitions (r3-fresh.txt, clause 4.9 "direct dependency (of a requirements class)" and 4.10 "indirect dependency (of a requirements class)", PDF page 18), with an additional paragraph: "The standardization target of the indirect dependency is different from the target of 'this requirements class' but it may be of the same or related standardization target type."

**[SOURCE] Observation on the definitions:** the Part 1 definition of "indirect dependency" is about a *different standardization target* (association, consumed product). It is **not** about transitivity. So in Part 1's vocabulary a chain A -> B -> core is neither a "direct" nor an "indirect" dependency of A on the core; the vocabulary has no term for it.

### 2.2 Part 2 (UML) uses "indirect" for the transitive case

`MS/24-065-part2-uml/sections/06-req-class.adoc` lines 60-64: "the conformance/requirements class associated to a package A will directly reference the conformance/requirements class associated to another package B, if and only if A is dependent on B. Indirect dependencies will be dealt with as the conformance classes cascade." Lines 93-97: "Other dependencies (indirect) will arise from the transitive closure of the above direct dependencies. That means if A depends on B, and B depends on C then A depends on C. Since these indirect dependencies will show up in the cascade of included conformance tests based solely on the direct dependencies, we can ignore them for effects on structure." The same text is in r3 (r3-fresh.txt lines 1383 and 1400, PDF pages 37-38) and in `24-065r1.html`.

**[SOURCE]** So within the ModSpec family, "direct" = the dependency edges a class itself carries ("directly reference"), and "indirect" is also used (in Part 2 only) for what follows from the transitive closure. This conflicts with the Part 1 definition of "indirect dependency" (different target). **[INFERENCE]** The ModSpec's own terminology is inconsistent; the Part 2 usage supports reading "direct" as "declared edge", and under that usage A -> B -> core gives "core" as an *indirect* dependency of A, not a direct one.

### 2.3 Fundamentals clause

`MS/sections/06-fundamentals.adoc` lines 80-89: "Conformance classes may contain dependencies on one another. These are represented by tests in one conformance class that state that another conformance class must be passed to qualify to pass this conformance class. In terms of requirements, that says that the dependent conformance class contains tests (by reference) for all requirements of the "included" conformance class. As defined in the ModSpec, one requirements class is dependent on another if the other is included through such a reference."

**[INFERENCE]** "Dependent" is defined by an explicit by-reference inclusion, i.e. a declared edge. This is closer to "listed" than to "reachable".

---

## 3. Surrounding normative text

All in `MS/sections/06-req-class.adoc` unless stated; r3 equivalents in r3-fresh.txt.

1. **Sentence the owner mentioned** (line 375-377; r3-fresh.txt 1234): "Since the core requirements class is contained (as a direct dependency) in each other requirements class with a similar standardization target type, the general recommendations are thus universal to all requirements classes." **[SOURCE]** The rationale is that general recommendations (Req 21: "All general recommendations for the standard SHALL be in the core.") reach every class. **[INFERENCE]** That rationale is satisfied by transitive reachability too; but the text still chooses to write "direct" in a parenthesis, and says "contained", which is by-reference inclusion (2.3). The sentence also scopes itself to classes "with a similar standardization target type".
2. **Req 4 commentary** (line 98-100): "In practice, the standardization target type of the core requirements class is the root of an inheritance tree where extensions all have the core's target type as an ancestor". **[SOURCE]** Here the STT relation is explicitly an ancestor (transitive) relation, whereas Req 22 part B says "direct".
3. **Req 17** (`REQ17_structure-requirements-classes.adoc`): "There SHALL be a natural structure to the requirements classes so that each may be implemented on top of any implementations of its dependencies and independent of its extensions."
4. **Req 18**: "No requirements class SHALL redefine the requirements of its dependencies, unless that redefinition is for an entity derived from but not contained in those dependencies."
5. **Req 12**: "A Conformance class SHALL specify any other conformance class upon which it is dependent and / That other conformance class SHALL be used to test the specified dependency." **[INFERENCE]** If "dependent" meant transitive reachability, Req 12 would force every class to list all ancestors, which no standard I read does (section 5). So "dependent" in Req 12 must mean direct. This supports "direct = declared edge" but says nothing about whether Req 22 requires the *core* to be one of the declared edges.
6. **Req 20, 21** (lines 339-349): define a core as "a separate requirements class with a corresponding conformance class" and put the general recommendations in it.
7. **Req 19 note, r3 only** (r3-fresh.txt 1217-1220; in `MS/original/06-req-class.adoc` line 600-603): "This means that a standard conformant to this standard predefines all of its possible profiles through the dependencies between the conformance classes. In essence, a profile of a conformant standard is precisely a transitive closure of a subset of requirements classes under the dependency relations." **[SOURCE]** This note is **not** in r7 (no "transitive" in r7html; checked by regex over the rendered text). It shows the authors modelled the dependency relation as declared edges whose closure defines profiles.
8. **Req 23, "Extensions are requirements classes"**. r3 (r3-fresh.txt 1250-1252): "Req 23 Each specification conformant to this standard shall consist of the core and some number of requirements classes defined as extensions to that core." Combined with the definition "extension: requirements class which has a direct dependency on another requirements class" (2.1), r3 Req 22 + Req 23 + the extension definition form a consistent triple: every non-core class is an extension of the core, i.e. has the core as a direct dependency. **[SOURCE, defect in r7]** In r7, `MS/requirements/core/REQ23_core-and-extensions.adoc` line 8 reads: "The standard _SHALL_ define and identify a core set of requirements as a separate requirements class with a corresponding conformance class." That is a verbatim duplicate of Req 20 (`REQ20_core-requirements-separate.adoc` line 8). **The published, approved r7 has the same defect**: `r7html` line 2727 (`id="req-23"`) reads "Requirement 23 Identifier /req/core/core-and-extensions Included in Requirements class 1: ... A The standard SHALL define and identify a core set of requirements as a separate requirements class with a corresponding conformance class.", and Req 20 at `r7html` line 2683 (`id="req-20"`) has the identical sentence. The r7 heading of its abstract test, "A.1.23. A standard is a core plus some number of extensions", still describes the old meaning. The original r7-draft text (commit 19419861, 2025-03-04) was "Each standard conformant to the ModSpec _SHALL_ consist of a core and some number of requirements classes defined as extensions to that core." It was overwritten in commit b8955012 (2025-08-23, `cmheazel`, message "Issue 88"). Issue #88 (by `heidivanparys`) only asked to remove "conformant to/with the ModSpec" and to say "the standard" instead of "every standard"; it did not ask for Req 23's meaning to change. **[INFERENCE]** This looks like an unintended copy-paste loss; worth reporting to the maintainers, because it removes the only requirement that links "extension" (= class with a direct dependency) to the core. It does not change Req 22.
9. **Extension (informative, Annex C)** `MS/sections/ac-definitions.adoc` lines 50-53: "an extension of a requirements class is an additional requirements class (the extension) that adds additional requirements to the first requirements class (the base requirements class being extended). The extension is said to be dependent on the base."
10. **Permissions 6-8** (`MS/permissions/core/PER006-008`): the core "MAY be partially or totally abstract", "MAY be a conformance class defined in another standard", and "MAY contain only recommendations". **[SOURCE]** These show that Req 22 applies to a core that may live in another standard, so a literal "list the core" can mean listing an external class.
11. **User guide** (`MS/mod-spec-user-guide/sections/01-informative.adoc` lines 394 and 472-473): "The requirements class table can include information on direct dependencies." and "A specific dependency is termed a `direct dependency`. A direct dependency is another requirements class (the dependency) whose requirements are defined to also be requirements of this requirements class." (line 470: "Dependencies can be general as in the above example or they can be more specific.") **[SOURCE]** The user guide equates "direct dependency" with what appears in the requirements class table; it says nothing on transitivity.
12. **Release notes** (`MS/release-notes-1-1/sections/*.adoc`, and `https://docs.ogc.org/DRAFTS/25-002.html`): no occurrence of "direct dependency", "transitive" or "indirect" (grep and regex). Nothing on Req 22.

---

## 4. Discussion by the ModSpec authors and the OGC community

Method: I downloaded every issue and pull request of `opengeospatial/ogc-modspec` (100 items, #1-#100) with their issue comments (`gh api repos/opengeospatial/ogc-modspec/issues/N` and `/comments`; PR review-comment endpoints returned 404 for items that are not PRs and were otherwise empty). Searched for "direct dependenc", "transitiv", "indirect", "req-class-not-core", "core as a", "subtype of that of the core", "Requirement 22", "REQ22". Also searched commits (`gh search commits`) and `gh search issues`/`gh search code` across the `opengeospatial` organisation.

**Result: no issue, PR or commit in ogc-modspec discusses Req 22's "direct dependency", transitivity, or the core-dependency rule.** The only hit for the search terms in the ogc-modspec issue tracker is #87 (below). Commit messages mentioning Req 22 are 59a35b5a (informative intro) and the file renames (56e4c7ee).

Relevant statements found:

1. **ogc-modspec #87** ("Part 1: proposal to remove "building block" and "module" definitions", opened by `heidivanparys`, open). She asks: "So https://docs.ogc.org/is/17-069r4/17-069r4.html#_requirements_class_core is not a building block because it depends on IETF standards?" `cnreediii` (2025-07-24): "The OAB discussed building blocks with respect to the ModSpec and agreed to the definition that a building block in the context of the ModSpec is a requirements class with no direct dependency on another requirements class." `rob-metalinkage` (2025-07-25): "...is incorrect - that was a "foundation building block"". `cnreediii` (2025-09-22): "Will change wording to foundation building block." **[SOURCE]** Relevance: "direct dependency" is used as "dependency on another requirements class declared by the class". The thread does not mention transitivity. **[INFERENCE]** A "foundation" with "no direct dependencies" implies a notion of direct as opposed to inherited, but this is not stated.
2. **opengeospatial/ogcapi-features #123** ("Clarify what "extension" to the core mean ...", 2018). `cportele` (2018-04-12): "In the OGC Specification Model "extension" is defined as "requirements class which has a direct dependency on another requirements class". I.e., a requirements class where the WFS 3.0 Core requirements class is a listed as a direct dependency." **[SOURCE]** `cportele`, a long-standing contributor to the OGC API - Features threads, reads "direct dependency" as "listed". `cmheazel` (same thread): "I'm not sure I would call the Mod-Spec short and clear, but it is normative."
3. **opengeospatial/ogcapi-coverages #181** ("Dependency on Core Requirements Class of OGC API - Common unspecified", opened by `ghobona` 2024-02-15, closed). `jerstlouis` (2024-02-15): "Any dependency of Common-2 - Collections would be implied by the dependency (only direct dependency are listed here), which currently only includes HTTP." SWG decision recorded by `jerstlouis` 2024-12-04: "SWG 2024-12-04: We will add a dependency in the Core requirements class to OGC API - Common - Part 1 :Core requirements class." **[SOURCE]** Gives the practitioner convention: only direct dependencies are listed, deeper ones are "implied". `ghobona` (OGC staff) asked for the dependency to be listed, but the issue text gives no ModSpec rationale. This was a missing dependency on a class not reachable at that time, not a transitive case.
4. **opengeospatial/ogcapi-records #300** (2023-2024, `jerstlouis`, `pvretano`, `cnreediii`, `cportele`). `pvretano` (2024-03-20): "THERE IS NO CORE mandatory requirement class in Records." `jerstlouis` (2024-03-20) quoted Req 20 from the ModSpec ("6.5.4 There is a Defined Core ...") and asked whether it applies. `cnreediii` (2024-03-21): "Yes, the ModSpec does specify that any OGC Standard have an identified core (6.5.4 There is a Defined Core). However, if you read the entire clause the core can be Abstract (As in CDB 2.0). The Core can also be specified as a mandatory dependency on another Standard, such as OGC API - Features. A fair amount of wiggle room." and "The ModSpec does need a bit of an update!" **[SOURCE]** This is the closest statement by a ModSpec author about enforcing the core clause: he calls it "a fair amount of wiggle room". It concerns Req 20/permissions, not part B of Req 22.
5. **OGC API - Features Part 4 (draft 20-002r1), clause 5.4** (`https://docs.ogc.org/DRAFTS/20-002r1.html`): "The requirements classes in this extension distinguish two types of dependencies to other Standards or requirements classes: First, there are the "direct dependencies". Every server implementing the requirements class has to conform to the referenced Standard or requirements class. In addition, requirements classes can also have "indirect dependencies". Servers implementing the requirements class do not have to conform to the referenced Standard or requirements class, but if they do, they have to conform to the requirements that identify the indirect dependency as a pre-condition for the normative statement." **[SOURCE]** (draft, not approved) In OGC API practice "indirect" means optional/conditional association, matching the Part 1 definition, not transitivity.
6. Searches that found nothing: `gh search issues` for "direct dependency" modspec, "transitive" "requirements class" modspec, `"core as a direct dependency"`, "requirement 22" modspec returned no relevant item beyond #87, #123, #181, #300 above (the latter two were found via other query terms). This is a search-API result, not an exhaustive guarantee. I could not read OGC mailing lists, OAB minutes, portal (portal.ogc.org) comment spreadsheets, or the "Public comments" (PR #95 body was read but contains no mention).

---

## 5. Empirical practice

### 5.1 Method

1. Data: the published HTML of approved OGC documents under `~/ogc-references/` (front matter checked: "Document stage: Approved" for all those in table A). Requirements Class tables are `<table>` elements whose first cell starts with "Requirements class". Script: `tools/rcdump.py` (dumps the tables) and `tools/analyze.py` (classifies). Output: `analysis.json` in the same directory.
2. For each class I read the identifier, and all rows labelled *Dependency*, *Prerequisite(s)*, *Conditional Dependency*, *Indirect Dependency/prerequisite*. A reference is resolved to a class of the same document by (a) the `href` fragment that points to the target class's table id, or (b) exact match of the full class URI, or (c) a relative `/req/name`. Unresolved relative references are printed (4 in SensorML/SWE, all harmless: concatenated cell text or typos in "Indirect prerequisite" rows).
3. Classification of each non-core class C with respect to the chosen core K:
   - **DIRECT**: K is in C's own Dependency/Prerequisite rows.
   - **TRANSITIVE**: K is not, but K is reachable by following Dependency/Prerequisite rows only.
   - **NONE**: K not reachable by any edge.
   - **INDIRECT-ONLY**: K reachable only by also following rows labelled "Indirect ..." (a different standardization target, per the ModSpec definition).
   - **CONDITIONAL**: K appears only in a "Conditional Dependency" row.
4. I spot-checked by eye the tables of Features 1, Common 1, SensorML 3.0, SWE Common 3.0, CS API 1 against the printed dumps (section 5.2 shows the individual classifications). The Processes check uses the AsciiDoc `inherit::` lines, script `tools/adoc_analyze.py`.

### 5.2 Core chosen in each document, and why

| Document | Core class used | Why |
|---|---|---|
| Features 1 (17-069r4) | `req/core` | class named "Core" |
| Common 1 (19-072) | `req/core` | class named "core" |
| Tiles 1 (20-057) | `req/core` | class named "Core" |
| Maps 1 (20-058) | `req/core` | class named "Core" |
| Records 1 (20-004r1) | `req/record-core` | **No class is named "core".** `record-core` is the only one with "core" in its name and the base the `records-api`, `crawlable-catalog` and `local-resources-catalog` classes list. `pvretano` wrote in ogcapi-records #300: "THERE IS NO CORE mandatory requirement class in Records." Therefore this choice is a judgement; with another choice the numbers change. (With this choice I reproduce the owner's "15 of 19": 18 non-core classes, 3 DIRECT, 6 TRANSITIVE + 9 NONE = 15 not-direct.) |
| JSON-FG (21-045r1) | `req/core` | class named "Core" |
| SensorML 3.0 (23-000) | `req/core` | "Clause 7, Requirements Class: Core Concepts (normative core)" in the document's own overview table |
| SWE Common 3.0 (24-014) | `req/core` | same text: "Clause 7, Requirements Class: Core Concepts (normative core)" |
| CS API 1 (23-001) | `req/api-common` | **No class is named "core".** `api-common` is "Requirements class 1" and the class every other class depends on (9 directly, 3 via another class). Judgement. |
| CS API 2 (23-002) | `req/api-common` | same pattern. Judgement. |
| CQL2 (21-065r2) | `req/basic-cql2` | **No class is named "core".** `basic-cql2` is the class the other 13 depend on, directly (11) or through `basic-spatial-functions` (2). Judgement. |
| GeoPose (21-056r11) | `req/global` | **No class is named "core".** Its description reads "Global requirements apply to all SDUs and Standardization Targets." Judgement; 12 classes list no prerequisite at all. |

### 5.3 Table A: approved documents with an identifiable core/base class (counts of non-core classes)

| Document (stage Approved) | Non-core | DIRECT | TRANSITIVE | NONE | INDIRECT-ONLY | CONDITIONAL | Literal reading flags |
|---|---|---|---|---|---|---|---|
| Features 1 (17-069r4) | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| Common 1 (19-072) | 4 | 0 | 0 | 4 | 0 | 0 | 4 |
| Tiles 1 (20-057) | 14 | 8 | 4 | 2 | 0 | 0 | 6 |
| Maps 1 (20-058) | 22 | 20 | 0 | 2 | 0 | 0 | 2 |
| Records 1 (20-004r1) | 18 | 3 | 6 | 9 | 0 | 0 | 15 |
| JSON-FG (21-045r1) | 7 | 5 | 0 | 0 | 1 | 1 | 2 |
| SensorML 3.0 (23-000) | 16 | 1 | 7 | 1 | 7 | 0 | 15 |
| SWE Common 3.0 (24-014) | 18 | 2 | 5 | 0 | 11 | 0 | 16 |
| CS API 1 (23-001) | 12 | 9 | 3 | 0 | 0 | 0 | 3 |
| CS API 2 (23-002) | 11 | 4 | 1 | 6 | 0 | 0 | 7 |
| CQL2 (21-065r2), core = `basic-cql2` (judgement: no class named core) | 13 | 11 | 2 | 0 | 0 | 0 | 2 |
| GeoPose (21-056r11), base = `global` (judgement: described as applying "to all SDUs and Standardization Targets") | 20 | 8 | 0 | 12 | 0 | 0 | 12 |
| **Total (12 documents)** | **160** | **76** | **28** | **36** | **19** | **1** | **84** |

Only 1 of the 12 documents (Features 1) fully satisfies the literal reading. 10 of 12 have at least two flagged classes (Maps 1 and CQL2 have exactly two each).

Details worth knowing (all from the HTML tables; `analysis.json` has the full graph):

- **Features 1**: every non-core class lists `Requirements Class "Core"` as `Dependency` (e.g. `html`: "Dependency | Requirements Class "Core" | #rc_core"). This is the pattern the literal reading expects.
- **Common 1**: `landing-page` and `oas30` list no requirements class at all; `html` and `json` list "Landing Page Requirements Class" only. 0 of 4 non-core classes list or reach the core.
- **CS API 1 transitive cases**: `subsystem` ("Prerequisite | Requirements class 2: /req/system"), `subdeployment` (-> `deployment`), `update` (-> `create-replace-delete`). 9 others list `Requirements class 1: /req/api-common`.
- **SensorML 3.0**: `model/coreProcess` lists `Requirements class 1: /req/core`; `model/simpleProcess` lists only `model/coreProcess`; etc. The JSON-Document classes (`json-core`, ...) have target type "JSON Document" and tie to the model classes through "Indirect prerequisite" rows. The core's target type is "Derived Model, Encoding, and Software Implementation", so JSON-Document classes are not subtypes of it (part A of Req 22 also cannot be applied literally). The same holds for SWE Common 3.0 (11 of 18 classes).
- **Records 1**: DIRECT: `records-api`, `crawlable-catalog`, `local-resources-catalog`. TRANSITIVE: `searchable-catalog` (-> `records-api`), `searchable-catalog/filtering`, `searchable-catalog/sorting`, `local-resources-catalog/query-parameters`, `.../filtering`, `.../sorting`. NONE: `record-collection`, `record-core-query-parameters`, `sorting`, `filtering`, `autodiscovery` (-> `record-collection`, which has no core link), `json`, `html`, `oas30`, `query-param-profile`.

**Local documents with requirements-class tables that Table A leaves out, and why:**

- COG (21-026): 5 classes, no class named core; `geotiff-format` is the root (3 of the other 4 list it directly, `optimized_geotiff` lists `geotiff-overviews` and `geotiff-keys`, i.e. transitive). Hand-read, not scripted; not added to the totals because the choice of root is arbitrary.
- SensorThings 1.1 (18-088) and Tasking (17-079r1): classes are organised as `req/datamodel/*` with dependencies on individual requirements (e.g. `.../common-control-information`), not on classes, and no core is designated. Not analysed.
- OMS 3.0 (20-082r4): UML-package style tables with "Imports" rows, 58 tables, no core. Not analysed.
- TMS 2.0 (17-083r4): 12 classes, no core; stage of the local copy not verified. Not analysed.
- Draft or unverified-stage documents (Features 4, Common 2, Pub/Sub 25-030, CS API 3 and 4): not in Table A; Features 4 and Common 2 are in Table B.
- Documents with a single class (Features 2, ModSpec r7/Part 2) have nothing to count.

Table A was therefore not "every local document": it is every local approved document where I could name a core or base class with a stated reason. Choosing differently for Records, CS API, CQL2 and GeoPose changes their rows.

### 5.4 Table B: parts whose core is in another document (core = the Part 1 or Common 1 core class)

Derived by reading the tables (not by `analyze.py`): numbers are the dependency rows printed in section 5.1 dumps.

| Document | Stage | Non-core | Lists the external core itself | Only through another class | Neither |
|---|---|---|---|---|---|
| Features 2 (18-058) | Approved | 1 (`crs`) | 1 | 0 | 0 |
| Features 3 (19-079r2) | Approved | 4 | 2 (`queryables-query-parameters`, `features-filter`) | 0 | 2 (`queryables` lists nothing; `filter` lists only `queryables`) |
| Features 4 (20-002r1-DRAFT) | Draft | 5 | 1 (`features`) | 0 | 4 |
| Common 2 (20-024-DRAFT) | Draft | 4 | 1 (`collections` lists Common 1 `req/core`) | 3 (`uad-collections`, `html`, `json` list `collections`) | 0 |

### 5.5 Table C: AsciiDoc source of a draft, and reconciliation with the owner's counts

OGC API - Processes Part 1 v2.0 (clone `.../scratchpad/real/ogcapi-processes`, HEAD 0f9c3d88, 2026-11-02, directory `core/requirements/`): 16 classes, core = `core`. Using the `inherit::` lines: 11 DIRECT, 3 TRANSITIVE (`remote-collections` -> `collection-input`; `oas30`, `oas31` -> `oas`), 1 NONE (`html`, whose `inherit::` lines are Common's html, an HTML5 reference and `/req/html`, i.e. **itself**; an apparent authoring error). That gives 4 flagged of 15 non-core.

**Why the owner sees "2 of 13" [partly INFERENCE, I have not seen the owner's checker output]:** the compiled XML `.../scratchpad/real/ogcapi-processes/18-062.xml` has 16 `type="class"` requirement elements, the same 16. Three of them, `rc_oas`, `rc_oas30`, `rc_oas31`, give their identifier as `<link target="https://www.opengis.net/spec/ogcapi-processes-1/2.0/req/oas"/>` (resp. `oas30`, `oas31`) inside the identifier cell, so a reader that expects a plain-text identifier would see 13 classes. Of the 13, exactly two are flagged: `html` (NONE) and `remote-collections` (TRANSITIVE). That matches "2 of 13" and means the three OpenAPI classes (1 direct, 2 transitive) are invisible to the owner's counts. This is the most likely cause; the other candidates (different snapshot, different class count) do not fit as well. `proc-compile.json` and `rec-compile.json` are only Metanorma compile logs (command, exit code, stderr), not checker output, so they cannot confirm it.

**Records:** I reproduce the owner's figure exactly. The 19 classes are the whole document; 18 are non-core; 3 DIRECT; 6 TRANSITIVE + 9 NONE = 15 not-direct ("15 of 19").

### 5.6 What practice tells us

**[SOURCE, counted]** Among approved standards, listing only the immediate parent is common (28 transitive cases) and standards that never reference the core exist (Common 1: 4 of 4). **[INFERENCE]** Either the OAB/SWG reviewers do not apply Req 22 part B literally, or they apply an interpretation that tolerates transitive reachability, or they do not apply it at all. The data cannot distinguish these. Practice is evidence about enforcement, not about meaning.

---

## 6. Conclusion

### 6.1 The two readings and the evidence for each

**Case for the literal reading (core must be in the class's own list):**

1. Part B says "direct dependency", not "dependency". The word came unchanged from r3 (2009) through the 2025 editorial passes (section 1). ATS 22 repeats it.
2. Part 1 defines "extension" as "requirements class which has a direct dependency on another requirements class", and r3 Req 23 required a standard to "consist of the core and some number of requirements classes defined as extensions to that core". Together with Req 22 B, that makes "has the core as a direct dependency" the defining property of an extension of the core (this is an inference; r3 does not say it in one sentence).
3. Part 2 says a class "will directly reference" its dependencies and that "Indirect dependencies will be dealt with as the conformance classes cascade". Req 27 speaks of classes that overlap "by reference". Fundamentals (06-fundamentals.adoc lines 86-89) defines "dependent" through a by-reference inclusion. All of these treat "direct" as a declared edge.
4. `cportele` (ogcapi-features #123): "a requirements class where the WFS 3.0 Core requirements class is a listed as a direct dependency". `jerstlouis` (ogcapi-coverages #181): "only direct dependency are listed here". Req 12 (a conformance class "SHALL specify any other conformance class upon which it is dependent") only works if "dependent" means direct, because otherwise every class would list all its ancestors (no standard does).
5. Part 3 of the ModSpec itself lists the core (the ModSpec 1.1 standard) as a "Dependency" row in both of its classes ("XML extension to the core" and "XML Schematron extension to the core"), although the Schematron class also depends on the XML class through REQ007. So the ModSpec's own extension that depends on another extension also lists the core directly (`MS/24-066-part3-xml/sections/06-req-class.adoc` lines 27-30 and 196-200). **[INFERENCE]** weak: these rows point to the whole ModSpec document, not to a requirements class.

**Case for the transitive reading (reachability suffices):**

1. **The Part 1 definition.** "Direct dependency" is defined as "another requirements class (the dependency) whose requirements are defined to also be requirements of this requirements class". If C depends on B and B depends on the core, the core's requirements are also requirements of C (the UML model says dependent classes "must be satisfied for this requirements class to be satisfied", `MS/models/ogc-modspec.lutaml` line 105-110, and ConformanceClass: "to pass the test for "a" a standardization target must also pass the test for "b""). The definition says nothing about hops, and its NOTE 1 ties "direct" to "the same standardization target as the current requirements class", not to path length. The only other notion Part 1 contrasts it with, "indirect dependency", is defined by a *different* standardization target. On that reading the core is a "direct dependency" of C because C and the core share a target, and C is not asked to repeat it.
2. The sentence that explains Req 22 pairs "(as a direct dependency)" with "each other requirements class with a similar standardization target type" and concludes "the general recommendations are thus universal to all requirements classes". That purpose is met by reachability.
3. Req 22 part A uses the transitive STT relation ("subtype", "ancestor" in the Req 4 commentary), and the Part 1 text calls the core's standardization target type the root of an inheritance tree. Reading part B in the same inheritance sense is natural.
4. ModSpec Part 2 and r3 Req 19 note model the dependency relation as one whose closure defines the profiles ("a profile of a conformant standard is precisely a transitive closure of a subset of requirements classes under the dependency relations"), and say indirect dependencies "show up in the cascade of included conformance tests based solely on the direct dependencies".
5. Practice (section 5): 28 classes reach the core only through another class and 36 not at all in approved documents; no approved document I read states a rule that these must change. `jerstlouis` calls deeper dependencies "implied". `cnreediii` describes the core clause as having "a fair amount of wiggle room" (stated about Req 20, not part B).

**Where they collide:** a "direct dependency" is not defined as "the one the class lists", but the word "direct" in Req 22 would be redundant on the transitive reading ("have the core as a dependency" would do), and the community reads it as "listed". The Part 1 "indirect" definition has no term for the chain case, and Part 2 uses "indirect" for exactly that case.

**My weighing [INFERENCE]:** the literal reading is somewhat better supported by wording and by every reader I found; the transitive reading is better supported by the definition and the purpose. I do not have a defensible probability, so I give none: **leans literal, genuinely ambiguous.** Practice shows the literal reading is not enforced, which is evidence about review, not about meaning.

### 6.2 Confidence

- That the text says "direct" and ATS 22 tests "direct": certain.
- That "direct" was meant as "listed in the class's own dependency list": leans yes, not settled (see 6.1).
- That OGC or the ModSpec maintainers would accept "transitive" as conforming: unknown. I found no statement by them either way. Do not present either reading as the official OGC position.

### 6.3 What only the maintainers/OGC can settle

Whether part B of Req 22 requires the core to be an *explicit* member of each non-core class's dependency list, or is satisfied when the core is a dependency of a dependency (is "contained" through the cascade). The text does not decide it, and the editors have not discussed it in public. Related defect to report: r7 Req 23 duplicates Req 20 (section 3, item 8).

### 6.4 One precise question for the maintainers

Suggested for the `opengeospatial/ogc-modspec` issue tracker (or to GitHub logins `cnreediii` and `cmheazel`, the most frequent committers to the Req 22 and `06-req-class.adoc` files in the commit log):

> In ModSpec 1.1 (08-131r7) Requirement 22 part B (/req/core/req-class-not-core-stt-subtype-of-core) says every non-core requirements class "SHALL have the core as a direct dependency", and Abstract Test 22 says "has the core as a direct dependency". If requirements class C lists only requirements class B as its dependency and B lists the core, C therefore depends on the core only transitively. Does C satisfy Requirement 22 part B, or must the core itself appear in C's own dependency list? If transitive is acceptable, should the requirement and ATS 22 say "direct or transitive dependency"?

### 6.5 Practical note for the checker (my suggestion, outside the question)

Report three states instead of one: core listed (pass), core reachable only through other classes (warn, reference Req 22 B), core not reachable (fail). Records 1, Tiles 1, CS API 1, SensorML 3.0, SWE Common 3.0 and CQL2 have transitive-only cases; Common 1, Maps 1, Records 1, CS API 2, Tiles 1, GeoPose and Processes (self-referencing `html`) have unreachable cases. Also tell users that the "core" has to be configured when a standard names none (Records, CS API).

---

## 7. Gaps and limits

- No access to OGC portal, OAB or SWG minutes, the OGC Architecture DWG archives, or mailing lists. The ModSpec GitHub PR/issue text is complete for ogc-modspec #1-#100 (comments included); PR review comments were not available/empty.
- GitHub search (`gh search`) is not exhaustive; I did not read all issues in other OGC repos.
- I did not read the full ModSpec 08-131r5 or r6 (not in the local material), so the history between r3 (2009) and the 2025 rewrite is not covered. Req 22 B is the same in r3 and r7.
- Approved-document tables were parsed from published HTML copies in `~/ogc-references/` (Tiles, Maps, Records are in `.../naming-authority/NamingAuthority/specification-elements/specifications/`; their front matter says Approved). I did not re-download from docs.ogc.org.
- The choice of "core" is a judgement for Records, CS API 1 and CS API 2 (5.2). Counts for those three are dependent on it.
- Table B and the COG note were derived by reading; Tables A and C by script. GeoPose and CQL2 were added after review, with the base/core chosen by me.
- The Processes difference is explained in 5.5 by inference from the compiled XML only; I did not see the owner's checker output.
- Whether the flagged standards were reviewed against Req 22 by the OAB is unknown.

---

## Summary (under 25 lines)

1. Verdict: the text leans literal ("direct dependency"), but the question is genuinely ambiguous; no probability offered. Only the maintainers/OGC can settle it.
2. Question for them: "In 08-131r7 Req 22 B / ATS 22, if class C lists only class B and B lists the core, does C satisfy 'has the core as a direct dependency', or must the core appear in C's own dependency list? If transitive is acceptable, should the wording say 'direct or transitive'?"
3. Req 22 (r7) B: "Every requirement class in the standard, with the exception of the core, SHALL have the core as a direct dependency." ATS 22 repeats it; method "Inspect the document to verify the above", no criterion. r3 has the same rule in one sentence.
4. Definitions: "direct dependency" = "another requirements class (the dependency) whose requirements are defined to also be requirements of this requirements class". "Indirect dependency" = a class with a different standardization target (not transitive). Part 2/r3 call the transitive closure "indirect". The vocabulary is inconsistent and has no term for a chain.
5. For literal: the word "direct", the "extension" definition, Part 2 "directly reference", `cportele` "listed as a direct dependency" (ogcapi-features #123), Req 12 only works with direct.
6. For transitive: the definition is satisfied by a chain (requirements of B include the core's), the stated rationale is met by reachability, Req 22 A is transitive by nature, practice does not enforce it.
7. No issue, PR or commit in ogc-modspec (#1-#100 read) discusses it. `cnreediii` (ogcapi-records #300) called the core clause "a fair amount of wiggle room".
8. Defect in the published r7: Req 23 (line 2727) duplicates Req 20; "core and extensions" was lost in commit b8955012 (2025-08-23, "Issue 88").
9. Empirical, 12 approved documents, 160 non-core classes: 76 list the core, 28 only transitively, 36 not at all, 19 only via "Indirect prerequisite" (different target type), 1 conditionally. Only Features 1 passes the literal reading fully. Records 1: 3 direct, 6 transitive, 9 none (15 of 19, matches the owner). Processes HEAD: 4 of 15 flagged; the owner's "2 of 13" is explained by 3 OpenAPI classes whose identifiers are links in the compiled XML.
10. Core choices that are judgement: Records (`record-core`), CS API (`api-common`), CQL2 (`basic-cql2`), GeoPose (`global`).
11. Suggest the checker report three states (listed / transitive only / unreachable) and make the core configurable.
