# Questions for the ModSpec maintainers / OGC: drafts for the owner to review and post

Status: **drafts, 2026-11-07. Nothing has been sent.** They were written by an AI agent from documents it read; the owner reviews, edits
and posts them under their own account. Each is written to stand alone so it can be pasted as one issue. Quotations were checked
against the published 08-131r7 HTML (`~/ogc-references/modspec/08-131r7.html`), the research notes in `docs/research/`, and (question 2
only) the public commit history on GitHub, read on 2026-11-07. Where a claim rests on something else, the draft says so.

Where to post: ModSpec issues go to `github.com/opengeospatial/ogc-modspec` (issues), questions 1, 2, 3, 4, 6 and 8. Question 5 is about
the draft Policy (OGC 25-001); the Policy sources are in the `opengeospatial/policy` repository, so open it there or ask OGC staff
which channel they prefer. **Not checked:** whether each tracker accepts outside issues, and whether the maintainers prefer one issue
or several. Questions 1 and 6 are close cousins (both ask what a "dependency" means) and could be one issue.

**Question 7 (added 2026-11-07)** is different in kind: it reports a probable typo in the Connected Systems API source, and goes to
`github.com/opengeospatial/ogcapi-connected-systems` (issues are enabled there, checked with the GitHub API on 2026-11-07). The file on its
default branch still had the same lines on that date; the repository's last push was 2026-10-08.

Do not name individual people in the issues (the research notes list frequent committers; whether to address anyone is the owner's call).

---

## 1. Requirement 22 B: is a chain of dependencies enough for "direct dependency"?

**Title:** Req 22 part B and ATS 22: does a transitive dependency on the core satisfy "direct dependency"?

Requirement 22 in 08-131r7 (`/req/core/req-class-not-core-stt-subtype-of-core`) has two parts. Part B reads: "Every requirement class in the
standard, with the exception of the core, SHALL have the core as a direct dependency." Abstract Test 22 says "...has the core as a
direct dependency" and gives the method "Inspect the document to verify the above."

Suppose requirements class C lists only class B as its dependency, and B lists the core. Then C depends on the core only
through B. Does C satisfy part B, or must the core appear in C's own dependency list?

What we found that bears on it:
- Part 1 defines "direct dependency" as "another requirements class (the dependency) whose requirements are defined to also be requirements
  of this requirements class", and defines "indirect dependency" as a class "with a different standardization target". Under those
  definitions a chain A to B to core is neither direct nor indirect.
- Part 2 (UML, 24-065r1) uses "indirect" for the transitive case: "Other dependencies (indirect) will arise from the transitive closure of
  the above direct dependencies."
- Practice varies. In 12 approved OGC documents with an identifiable core class (160 non-core classes), 76 list the core directly, 28
  reach it only through other classes, and 36 do not reach it at all (our counting; method and tables in our repository,
  `docs/research/Req22-transitive-dependency.md`, which you can link).

Questions: (a) Is a transitive dependency acceptable for part B? (b) If it is, should Req 22 B and ATS 22 say "direct or transitive
dependency"? (c) If it is not, should ATS 22 say how to decide?

Why we ask: a checker has to pick a reading. Ours implements the literal one (the core must be listed) and reports transitive-only cases
as a separate state so users can tell them apart.

---

## 2. Requirement 23 in the published r7 repeats Requirement 20

**Title:** Req 23 (`/req/core/core-and-extensions`) has the same text as Req 20: intended?

In the published 08-131r7 (approved, published 2026-05-21), Requirement 20 (`/req/core/core-requirements-separate`) reads: "The standard
SHALL define and identify a core set of requirements as a separate requirements class with a corresponding conformance class."
Requirement 23 (`/req/core/core-and-extensions`) reads exactly the same. The identifiers differ; the text does not.

The repository history (`opengeospatial/ogc-modspec`, file `sources/requirements/core/REQ23_core-and-extensions.adoc`) shows how: commit
`b8955012` ("Issue 88", 2025-08-23) changed Req 23's text from
"Each standard conformant to the ModSpec SHALL consist of a core and some number of requirements classes defined as extensions to that core."
to the Req 20 sentence above, in the same commit that changed Req 20's "Every standard" to "The standard". That looks like a copy-and-paste
slip, but we cannot tell the intent from outside.

Questions: (a) Was Req 23 meant to keep its original text ("a core and some number of requirements classes defined as extensions")?
(b) If so, is a correction planned, and would it be a new revision? (c) ATS 23 targets the same identifier; should it be checked too?

Why we ask: checkers key requirements by identifier and test by text; two requirements with the same text cannot be told apart by what they
require, and the original Req 23 text, which says every conformant standard consists of a core plus extensions, no longer appears in the published document.

---

## 3. Which ModSpec Parts are "relevant" for a standard with a UML model and JSON encodings?

**Title:** "Core Standard and relevant Parts": which Parts apply to a UML conceptual model with JSON encodings?

The draft Policy (OGC 25-001, status Draft) says a new OGC Standard "SHALL comply with the requirements stated in the OGC ModSpec Core
Standard and relevant Parts." "Relevant" is not defined. Parts 2 (UML) and 3 (XML), both approved edition 1.1, call themselves
optional.

Our reading from the texts: a UML model makes Part 2 relevant; an XML Schema makes Part 3 relevant; a JSON encoding is covered by
neither Part, and Part 1 clause 9 says alternative mechanisms are judged "solely on the structure of their conformance test suite".

Questions: (a) For a standard that defines a conceptual model in UML and encodings in JSON (no XSD), is Part 2 required, and is anything
required for the JSON side beyond Part 1? (b) Who decides which Parts are relevant: the standard's author, the SWG, or OGC staff?

Why we ask: it decides which structural rules a checker may treat as mandatory. Today ours makes the UML-package rules opt-in.

---

## 4. What is the URI of a conformance class, for Part 3 REQ004?

**Title:** Part 3 REQ004: which URI goes in `appinfo` for "the associated conformance test class"?

Part 3 (24-066r1) REQ004 says the all-components schema document "SHALL indicate the URI of the associated conformance test class in the
schema/annotation/appinfo element." Neither Part 2 nor Part 3 defines a URI form for a conformance class or for a conformance test:
Part 3's test heading says only "A reference to the URI of the test suite in AppInfo", and neither Part gives its tests or conformance
classes identifiers of the `/conf/...` kind.

Questions: (a) Is the intended value the full URI of the conformance class (the standard's namespace plus the class's `/conf/...`
identifier), the URI of a test suite, or something else? (b) If the first, can Part 3 say so?

A related observation: Part 3's REQ006 repeats the text of REQ004 (`no-element-modification` and `all-components-uri`), which looks like
the same kind of slip as question 2.

---

## 5. Is the draft Policy enforceable now, and which ISO Directives edition does clause 7 mean?

**Title:** OGC 25-001 (draft ModSpec Policy): status, and which edition of ISO/IEC Directives Part 2 clause 7 applies?

The Policy source we read has `:status: Draft` and an issue date of `2026-xx-xx`. It mandates ModSpec for new OGC Standards and
requires an Abstract Test Suite in a normative annex, and it sends verbal forms to ISO/IEC Directives Part 2, clause 7.

Questions: (a) Is the draft already applied to SWG submissions, or only once approved? (b) Which edition of ISO/IEC Directives Part 2 is
meant by "current"?

Why we ask: we read clause 7 from edition 9.0 (2021-05, the redline copy) and did not check any later edition. Our checker treats
`shall` / `should` / `may` as the verbal forms and flags `must` in a provision; if a later edition differs, that rule is wrong.
Separately, the Policy's paragraph on Part 2 says the mapping "should follow the logical mechanism described in Part 1 of the ModSpec";
that probably means Part 2 (our guess; please confirm or ignore).

---

## 6. Requirement 12: does it cover a dependency that exists only through the requirements class?

**Title:** Req 12: must a conformance class list a dependency that follows from its requirements class's dependencies?

Requirement 12 (`/req/core/con-class-dependencies`) reads: "A. A Conformance class SHALL specify any other conformance class upon which it
is dependent and B. That other conformance class SHALL be used to test the specified dependency. Such referenced conformance classes may be
in the same standard or may be a conformance class of another standard." Requirement 8 puts requirements classes and conformance classes
in one-to-one correspondence.

Suppose requirements class R2 lists requirements class R1 as a dependency, and conformance class C2 corresponds to R2 and C1 to R1. Must C2
also state C1 as a dependency in its own text, or is it enough that the dependency is stated on R2 and the classes correspond one to
one?

We have not surveyed how approved documents handle this, so we offer no count.

Why we ask: in our record format a conformance class's in-document dependencies are derived from its requirements class, and only external
ones are written by hand. We deliberately wrote no rule that every conformance class must list each dependency, because it would encode
one reading of Req 12 and would flag documents that OGC has already approved.

---

## 7. Connected Systems API Parts 1 and 2: some terms cite a bibliography key that does not exist

**Title:** Terms and definitions: source keys `SOSA/SSN`, `ISO19101` and `ISO19143` have no bibliography entry (Parts 1 and 2)

In `api/part1/standard/sections/clause_4_terms_and_definitions.adoc` the Actuator entry reads
`<<SOSA/SSN, SOSA-SSN, http://www.w3.org/ns/sosa/Actuator[Actuator Class]>>` (line 15). In this form the first item is the bibliography key and
the second the display text. Clause 3 defines the key `SOSA-SSN`, which the other SOSA entries use (for example
`<<SOSA-SSN, SOSA/SSN, http://www.w3.org/ns/sosa/Observation[Observation Class]>>`), so the first item here looks swapped with the second.
Part 2 has the same form on two entries, Actuation (line 15) and Actuator (line 22), of
`api/part2/standard/sections/clause_4_terms_and_definitions.adoc`.

Metanorma 2.5.16 reports each of these when the document is compiled (STANDOC_32, "... does not have a corresponding anchor ID in the
bibliography"): in Part 1 for `SOSA/SSN`, `ISO19101` and `ISO19143`; in Part 2 for `SOSA/SSN` (twice), `ISO19101` and `ISO19143`. The compiled
XML carries `bibitemid="SOSA/SSN"` and so on. I did not find entries for `ISO19101` and `ISO19143` in the clause 3 list or the annex
bibliography file; if they are defined somewhere else, please disregard that part.

Question: is swapping the two items on the three SOSA lines (so the key is `SOSA-SSN`) the intended fix, and are `ISO19101` and `ISO19143`
meant to be bibliography entries?

Why we ask: we read these documents to test a tool that checks the terms of a standard against its source records, and it flagged the keys.
The text and links look correct to a reader; only the link from the citation to the bibliography is affected. Found with the v1.0 source
(commit 8e03b236) and the same lines on `master` on 2026-11-07.

---

## 8. Indirect dependency within one standard: recorded in the conformance class only, or also in the requirements class?

**Title:** Req 12 and an indirect dependency between two requirements classes of the same standard: where is it recorded?

Part 1 (08-131r7) defines two kinds of dependency. Clause 6.1.3: a **direct dependency** is "another requirements class (the dependency) whose requirements are defined to also be requirements of this requirements class",
and "will have the same standardization target as the current requirements class". Clause 6.1.5: an **indirect dependency** is a "requirements class with a different standardization target which is used by, produced by, or
associated with the implementation of this requirements class", and "Such a requirement may be stated as the associated licensing service has a certificate of conformance of a particular kind." Requirement 12 says: "A. A Conformance
class SHALL specify any other conformance class upon which it is dependent and B. That other conformance class SHALL be used to test the specified dependency. Such referenced conformance classes may be in the same standard or may be a
conformance class of another standard", and gives an indirect-dependency example (a service whose output must conform to another standard's conformance class).

Our situation, in generic terms: one standard has requirements class A, whose standardization target is a specification document, and requirements class B, whose target is a binding document that must refer to a document conforming
to A. Both targets are subtypes of the core's target (Requirement 22 A). B depends on A indirectly in the sense of 6.1.5: B states "the referenced document conforms to class A", and a test of B uses A's conformance class.

Questions: (a) Is the intended place to record this the conformance class of B (Requirement 12 A: B's conformance class specifies A's conformance class as a dependency), with the requirements class B listing nothing? (b) Or should
requirements class B also list A in its own dependency list (the `inherit` entries in Metanorma markup)? If so, does listing it make A's requirements "also requirements of" B, which 6.1.3 says is a direct dependency for the
same target, and which would then apply A's requirements to binding documents? (c) Does Metanorma's `inherit` carry any meaning for a class with a different target, or is it only for direct dependencies?

Why we ask: our checker reads `inherit` as a graph of direct dependencies (cycle checks; Requirement 22 B: the core as a direct dependency) and derives the dependencies of each conformance class from it. An indirect dependency
cannot be derived that way, so the format needs a second way to write it, and which way depends on the answer. We have not found published examples that settle it; we have not surveyed approved documents.

