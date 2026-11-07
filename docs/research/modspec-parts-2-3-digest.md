# Digest of OGC ModSpec Part 2 (UML, 24-065r1) and Part 3 (XML, 24-066r1)

Prepared 2026-11-06. Read-only study. Nothing under ~/ogc-references was modified or executed.

## 0. Sources and method

Primary (pinned clone, git HEAD `726e64744e909899ba36174dde0fcbee6fde4f85`, working tree clean), referred to below as `$CLONE`:
`docs/references/git/opengeospatial-ogc-modspec/sources/`

- Part 2: `$CLONE/24-065-part2-uml/{24-065r1.adoc, sections/*.adoc, 24-065r1.xml, 24-065r1.html}`
- Part 3: `$CLONE/24-066-part3-xml/{24-066r1.adoc, sections/*.adoc, 24-066r1.xml, 24-066r1.html}`
- Standalone HTML renditions: `https://docs.ogc.org/pol/24-065r1/24-065r1.html`, `https://docs.ogc.org/pol/24-066r1/24-066r1.html`
- Part 1 context (not re-digested): `$CLONE/sections/`, `$CLONE/requirements/`, `$CLONE/abstract_tests/`, `$CLONE/recommendations/`, `$CLONE/permissions/`, `$CLONE/08-131r7.xml`
- Policy: `$CLONE/ogc-modspec-policy/{document.adoc,00-preface.adoc,06-policy.adoc}`

Cross-checks performed:
- The scratchpad copy of both Part directories (`.../scratchpad/real/ogc-modspec/sources/24-06{5,6}-*`) is byte-identical to the clone (`diff -rq` empty).
- The standalone Part 2 HTML is byte-identical to the clone's HTML.
- The standalone Part 3 HTML differs from the clone's HTML only in generated element ids and in one keyword: `oogcdoc` (standalone) versus `ogcdoc` (clone, adoc, XML). This is a typo in the standalone rendition only. I diffed the full id-stripped text, not just the head of the diff.
- Every requirement and permission table in both compiled XMLs was compared with the HTML text and with the adoc. The normative text is the same in all three, including the defects listed in section 5. The compiled output differs from the adoc only where section 5 says so (the dropped normative-references paragraph, the cross-references that fail to resolve, and the metadata).
- The authored `.adoc` and the compiled `.xml` otherwise agree on the text of every requirement.

Conventions in this report:
- Quotations are verbatim. In the adoc, `_SHALL_` is emphasis markup. In the XML it is `<em>SHALL</em>`. I print it as SHALL.
- `P2` and `P3` mean Part 2 and Part 3. "HTML §n" means the clause number as rendered in the HTML. These differ from the adoc, which has no numbers.
- Line numbers refer to the adoc files under `$CLONE/24-06x-*/sections/`.

---

## 1. Document facts

### 1.1 Part 2: "The ModSpec Model - Part 2: UML"

| Item | Value (source) |
|---|---|
| Document number | 24-065r1 (`24-065r1.adoc` `:docnumber:`; XML `<docidentifier type="ogc-internal">`) |
| External identifier | `http://www.opengis.net/doc/POL/ModSpec-part2/1.1` |
| Edition | 1.1 (`:edition: 1.1`) |
| Status | `:status: approved` (XML `<stage>approved</stage>`; HTML "Approved", "OGC Standard") |
| Dates | received 2025-10-20; issued (HTML "Approval Date") 2026-03-05; published 2026-05-21 |
| Other metadata | `:draft: 3.0`, XML `<revision-date>##</revision-date>` (placeholder). `:docsubtype: logical-model` in the adoc, but XML `<subdoctype>implementation</subdoctype>` and HTML "Document subtype: Implementation". |
| Editors | Carl Reed, John Herring |
| Scope (quote, `01-scope.adoc`) | "This Part 2 of the ModSpec defines the requirement class for using UML. The use case is if the organizing mechanism for the data model used in a standard is an object model, then the mapping from parts of the model to the requirements classes should follow the logical mechanism described in Part 2 of the ModSpec." |
| Self-description | Foreword: "This Part 2 specifies the optional UML Requirements Class." Preface: "defines an optional ModSpec requirements class for UML." |

Relation to Part 1:
- Part 1 (08-131r7) defines exactly one requirements class, Core. Its identifier is `https://www.opengis.net/spec/modspec-1/1.1/req/req-class-core` and its target-type is `Standard` (`$CLONE/requirements/requirements_class_core.adoc`). Its conformance class is `.../conf/conf-class-core` (`$CLONE/abstract_tests/ATS_class_core.adoc`).
- Part 2 says it is an extension of that Core. `02-conformance.adoc`: "There is one conformance class for this document for: . Standards using UML to state requirements, extending the core." and "This requirements class is an extension of the Core presented in the ModSpec Core Standard".
- Part 2 never cites the Core class by URI. Its "Dependency" row is a document citation (see section 5, item 2).

Part 2's own requirements class (one only), as it appears in the table at `06-req-class.adoc` lines 30-47 (HTML §7.2, Table 1):

| Field | Value as written |
|---|---|
| Name | "Requirements Class - UML extension to the core" |
| Identifier row | `/req/core/data-representation` (same string in all three Part 2/3 class tables; see 5.1) |
| Target | "ModSpec Conformant UML Model" |
| Dependency | "OGC ModSpec Version 1.1 [OGC 25-003r1]" |
| Members | REQ001 to REQ011 |
| Conformance test class | "Conformance test class: UML model extends The Standard" (anchor `annex-A-1`, HTML §8, subclauses 8.1 to 8.11) |

Standardization target type: the "Target" row, "ModSpec Conformant UML Model". No `target-type::` field exists in Parts 2/3.

### 1.2 Part 3: "The ModSpec Model - Part 3: XML"

| Item | Value (source) |
|---|---|
| Document number | 24-066r1 |
| External identifier | `http://www.opengis.net/doc/POL/ModSpec-part3/1.1` |
| Edition | 1.1 |
| Status | approved (same dates, draft 3.0, `revision-date ##`, subdoctype mismatch as Part 2) |
| Editors | Carl Reed, John Herring |
| Scope (quote, `01-scope.adoc`) | "Part 3 of the ModSpec defines the requirements for using XML. The XML related requirements classes cover any standard which has as one of its purposes the introduction of a new XML schema. Such a standard would normally define the schema, all of its components, and its intended uses." |
| Self-description | Foreword: "This Part 3 specifies the optional XML Requirements Class." Preface: "defines an optional requirements class for the XML model extension the ModSpec core." |
| Conformance text (`02-conformance.adoc`) | "There are two conformance classes in this document for: . Standards using XML to state requirements, extending the core; and . Standards using Schematron." Annex A in fact contains three test classes (5.6). |

Part 3 has three requirements classes. The clause numbering below is the HTML numbering.

| Class | Name as written | Location | Class table? | Members | Target | Conformance test class (HTML §) |
|---|---|---|---|---|---|---|
| A | "Requirements Class - XML extension to the core" (heading: "Requirements class: The XML schema extension to the core"). The table has anchor `xml-model-conformance-class`. | §7.1.1, Table 1 | yes, `06-req-class.adoc` lines 24-37 | REQ001 to REQ006; PER001 and PER002 appear in the clause but not in the table | "ModSpec Conformant XML Model" | "Conformance test class: XML schema" (§8, 8.1 to 8.6) |
| B | "Requirements Class - XML Schematron extension to the core" (heading: "Optional Requirements class: Schematron extension") | §7.1.2, Table 10 | yes, lines 197-208 | REQ007, REQ008, REQ010, REQ011, REQ012 | "ModSpec Conformant XML Model" | "Conformance test class: Schematron" (§9, 9.1 to 9.6) |
| C | (heading only) "Optional Requirements class: XML meta-schema extension to the ModSpec Core." | §7.1.3 | **none** (no identifier, target or dependency row) | REQ013, REQ014 | not stated | "Conformance Class: XML meta-schema" (§10, 10.1 and 10.2) |

- Class A's "Dependency" row reads "OGC ModSpec Version 1.1 [25-003r1]".
- Class B's "Dependency" row reads "OGC ModSpec Version 1.1 (need proper title and document number)". This is an editorial placeholder left in the published text.
- Part 3 also says: "First the schema must be defined within the bounds of the XML schema requirements class." Class B therefore depends on class A, but nothing in a "Dependency" row says so.

---

## 2. Table of requirements, recommendations and permissions

How to read the table:
- **ID**: the label (REQ00n, PER00n) plus the identifier in the body of the requirement, which I treat as primary. Where the summary table in the same document spells the identifier differently, the variant is shown after "table:".
- **Kind**: R = requirement, P = permission. There are no labelled recommendations in either Part.
- **Test**: neither Part has abstract-test identifiers. There are no `/conf/...` URIs and no `[abstract_test]` records. Each test is an unnumbered subclause of the (non-annex) test clause. I locate it by its HTML clause number, its heading, and the `Reference:` cross-reference that links it to a requirement. I mapped tests by their `Reference:` target, not by heading. All tests use "Test Method: Inspect the document to verify the above." and "Test Type: Conformance."
- **Class**: for P2, "UML class". For P3, "A", "B" or "C" as in 1.2.
- **Classification** describes how one would check a **target standard** (for example a modeling-language standard) against the provision. It does not describe checking Parts 2/3 themselves.
  - MECHANICAL: decidable from structured requirement records, or from the compiled Metanorma XML of the target standard, alone.
  - MODEL: needs inspection of the target's UML model or XML schema, usually cross-referenced to the requirement records.
  - HUMAN: needs judgement.
  - "MECHANICAL\*" means the check is mechanical only if the records carry a dependency declaration. The Part 1 record examples (`requirements_class`: `identifier`, `target-type`, `requirement`; `conformance_class`: `identifier`, `target`, `abstract-test`) show no such field. See section 3.

### 2.1 Part 2 (UML), HTML §7.2, all in the single UML class

| ID | Kind | Normative text (verbatim) | Test (locator; Reference) | Classification |
|---|---|---|---|---|
| REQ001 `/req/part2/uml/conformance-with-core` | R | "An implementation passing the UML conformance test class SHALL first pass the ModSpec core conformance test class" (no final full stop in source) | HTML §8.1 "Dependency on Core"; Reference `<<req-01>>` | MECHANICAL\*: only the declared dependency of the UML conformance class on the core conformance class is visible in records; "first pass" is an outcome. |
| REQ002 `/req/part2/uml/object-model` | R | "To be conformant to this UML requirements class, UML SHALL be used to express the object model, either as the core mechanism of the standard or as a normative adjunct to formally explain the standard in a model" (no final full stop) | HTML §8.2 "The UML model is normative"; Reference `<<req-02>>` | HUMAN: judging that UML is the core mechanism or a normative adjunct. Existence of a UML artefact is MODEL. |
| REQ003 `/req/part2/uml/dependency-graph` | R | "A UML model SHALL have an explicit dependency graph for the leaf packages and external packages used by the standard consistent with the way their classifiers use those of other packages" (no final full stop). NOTE in source: "External packages having predated the current version of the standard will not normally have dependencies to packages within the standard." | HTML §8.3 "Dependency graph must be explicit"; Reference `<<req-03>>` | MODEL: package dependency relations must be compared with classifier usage (attribute types, associations, generalizations). |
| REQ004 `/req/part2/uml/leaf-model` (table: `/req/part2/uml/leaf-package`) | R | "A UML leaf package SHALL be associated directly to only one requirements class." | HTML §8.4 "Leaf packages in only one requirements class"; Reference `<<req-04>>` | MODEL: needs a package to class association, which ModSpec does not define how to record. |
| REQ005 `/req/part2/uml/class-package` | R | "Each requirements class shall be associated to a unique package in the model and include either directly or by a dependency any requirement associated to any of its subpackages." (lowercase "shall"; see 5.9) | HTML §8.5 "Requirements class associated to a unique package"; Reference `<<req-05>>` | MODEL: package to class association; "include ... by a dependency" needs HUMAN reading. |
| REQ006 `/req/part2/uml/to-leaf` | R | "A requirements class SHALL be associated to some number of complete leaf packages and all classes and constraints in those packages." | HTML §8.6 "A requirements class contains complete leaf packages"; Reference `<<req-06>>` | MODEL: constraints (OCL or otherwise) must travel with their package. |
| REQ007 `/req/part2/uml/common-req-classe` (table: `/req/part2/uml/common-req-classes`) | R | "Classes that are common to all requirements classes SHALL be in a package associated to the core requirements class." Following prose: "This is actually a derived requirement and is repeated here for emphasis." | HTML §8.7 "Classes common to all requirement classes are in the core"; Reference `<<req-07>>.` | MODEL: "common to all" is computable from the dependency graph but is not defined. |
| REQ008 `/req/part2/uml/source-target` | R | Parts A and B: "A: In the UML model, if a "source" package is dependent on a "target" package then their requirements class SHALL be equal or" / "B: The source package's class SHALL be an extension of the target package's class." | HTML §8.8 "Package dependencies become requirements class extensions"; Reference `<<req-08>>.` | MODEL: cross-check of the package dependency graph against the requirements-class extension graph in the records. A and B are alternatives; see 5.8. |
| REQ009 `/req/part2/uml/leaf-package-dependency` | R | "If one leaf package is dependent on another leaf package, then the requirements class of the first SHALL be the same or an extension of the requirements class of the second." | HTML §8.9 "Dependencies in packages are reflected in dependencies in requirements classes"; Reference `<<req-09>>.` | MODEL: same cross-check as REQ008, restricted to leaf packages. |
| REQ010 `/req/part2/uml/two-way-dependency` | R | "If two packages have a two-way dependency (a "co-dependency"), they SHALL be associated to the same requirements class." Following prose: "For example, if two classes have a two-way navigable association, then these two classes must be (transitively) in the same conformance requirements class package." | HTML §8.10 "Co-dependent packages are in the same requirements class"; Reference `<<req-10>>` | MODEL: find cycles in the package dependency graph. |
| REQ011 `/req/part2/uml/segregate-into-leaf-packages` | R | "The UML model SHALL segregate all classes into leaf packages." | HTML §8.11 "All classes are in leaf packages"; Reference `<<req-11>>` | MODEL: no package may contain both classes and subpackages. |

### 2.2 Unlabelled normative prose in Part 2 (no identifier in source)

These statements are not in a requirement block, have no REQ/REC/PER label and no test. I did not assign them identifiers.

| Location | Verbatim | Apparent kind | Classification |
|---|---|---|---|
| `06-req-class.adoc` lines 174-177 (bold, highlighted, introduced by "the model then satisfies the following recommendation:") | "Each requirements class in a conformant standard should be associated to one and only one UML package (which may contain sub-packages for a finer level of structure). If the core requirements class contains only recommendations, it may be an exception to this." | recommendation (SHOULD) with a permitted exception | MODEL |
| lines 60-64 | "Assuming all legitimate direct package dependencies are included in the UML model, the conformance/requirements class associated to a package A will directly reference the conformance/requirements class associated to another package B, if and only if A is dependent on B. Indirect dependencies will be dealt with as the conformance classes cascade." | implied requirement ("will ... if and only if"), stronger than REQ008/REQ009 | MODEL |
| lines 66-67 | "This clause uses UML terminology, but other object modeling languages and, if needed, the object code itself can be mapped to a UML model." | implied permission | HUMAN |
| line 48 | "Any conformant UML extension will comply with the ModSpec Core requirements class." | restates REQ001 | n/a |
| lines 202-208 | "Although there is nothing to demand it, it is a common practice to move all classes down the hierarchy to leaf packages. Leaf packages are those that contain only classes (that is, contain no smaller subpackages). Classes can act as packages in the sense that a UML class can contain a locally defined class whose scope is the class itself. For our purposes, we will consider a class and its contained local classes to all be in the package of the original class." | definition of "leaf package" and "package of a class" (informative lead-in contradicts REQ011; see 5.10) | MODEL |
| lines 155-156 | "In UML, source and target dependency relations are defined in such a way that the source of the relation is dependent on the target of the relation." | definition | n/a |
| lines 150-153 | "By Clause <<req-22>> in the Core, only classes in the source requirements class will be affected by the requirement." | claim about Part 1 that does not match Part 1 (see 5.7) | n/a |

### 2.3 Part 3 (XML), classes A, B and C

| ID | Kind | Class | Normative text (verbatim) | Test (locator; Reference) | Classification |
|---|---|---|---|---|---|
| REQ001 `/req/part3/xml/conformance-with-core` | R | A | "An implementation passing the XML conformance test class SHALL first pass the ModSpec Core conformance test class" (no final full stop) | HTML §8.1 "Dependency on Core"; `<<req-01>>` | MECHANICAL\* (as P2 REQ001) |
| REQ002 `/req/part3/xml/w3c-xml` | R | A | "An implementation passing the XML schema conformance test class SHALL first pass the W3C Recommendation for XML schema." | HTML §8.2 "Dependency on W3C XML schema"; `<<req-02>>` | MODEL: schema validity against XML Schema, run by a schema-aware tool. Which version is meant is unclear (see 5.19). |
| REQ003 `/req/part3/xml/single-xml-space` | R | A | "If a standard conformant to the XML schema conformance class defines a set of data schemas, all components (e.g., elements, attributes, types ...) associated with a single conformance test class SHALL be scoped to a single XML namespace." | HTML §8.3 "A requirements class corresponds to a single XML namespace"; `<<req-03>>` | MODEL: namespace of every component compared with the class membership in the records. |
| REQ004 `/req/part3/xml/all-components-uri` | R | A | "The all-components schema document for an XML Schema SHALL indicate the URI of the associated conformance test class in the schema/annotation/appinfo element." | HTML §8.4 "A reference to the URI of the test suite in AppInfo"; `<<req-04>>` | MODEL: read `xs:schema/xs:annotation/xs:appinfo` and compare it with the conformance class identifier in the records. Part 3 defines no conformance-class URI form (5.20). |
| REQ005 `/req/part3/xml/direct dependency` (contains a space; table: `/req/part3/xml/direct-dependency`) | R | A | "If a standard conformant to the XML schema conformance class defines a direct dependency from one requirement class to another, then a standardization target of the corresponding conformance test class SHALL import a schema that has passed the associated conformance test class (dependency) or shall itself pass the associated conformance test class." NOTE: "This implies that the value of the schemaLocation on the `<import>` element will refer to the all-components schema document." | HTML §8.5 "Direct dependencies become schema imports"; `<<req-05>>` | MODEL: `xs:import` graph versus the requirements-class dependency graph. |
| PER001 `/per/part3/xml/schema-assembly` | P | A (in clause, not in the table) | "An all-components schema document MAY be assembled by inclusion of documents that describe subsets of the components associated with the conformance test class." | none (permissions are not tested) | n/a: a permission has no failing condition. Tooling must allow `xs:include` inside the all-components document. |
| REQ006 `/req/part3/xml/no-element-modification` | R | A | "The all-components schema document for an XML Schema SHALL indicate the URI of the associated conformance test class in the schema/annotation/appinfo element." **This is word for word the text of REQ004; quoted as written, not repaired.** | HTML §8.6 "No requirements class modifies or redefines elements in another namespace"; `<<req-06>>`. Test text: "No requirements class in a standard conformant to the XML schema conformance class shall modify elements, types or any other requirement from a namespace to which it is not associated." The test says something different from the requirement. | MODEL. What is checkable depends on whether the text or the test (identifier and test text) governs. |
| PER002 `/per/part3/xml/add-constraints` | P | A (in clause, not in the table) | "Requirements may add constraints." (lowercase "may"). Following prose: "This allows extensions to restrict the following. 1. Usage of existing elements, but only if their use was originally optional. ... 2. The type of existing elements, to sub-types of the original elements." | none | n/a: a permission. Judging whether an extension stays inside the two listed freedoms is MODEL or HUMAN. |
| REQ007 `/req/part3/xml/schematron-xml-schema` | R | B | "A standard passing the Schematron conformance test class SHALL also define or reference an XML schema that shall pass the XML schema conformance class from this standard." | HTML §9.1 "Dependency on XML Schema conformance test class"; `<<req-07>>` | MODEL |
| REQ008 `/req/part3/xml/sch-pattern-constraints` | R | B | Parts A and B: "A: Each sch:assert element SHALL implement constraints described in no more than one requirement." / "B: Each requirement SHALL be implemented by no more than one sch:pattern." NOTE: "Requirement 9 was removed in the ModSpec version 1.1 as this requirement is present in the latest Schematron RelaxNG schema." | HTML §9.2 "Each schematron pattern element implements one requirement"; `<<req-08>>`. Test text says `sch:pattern` in both sentences, where A says `sch:assert`. | MODEL, and HUMAN where no link from assert or pattern to a requirement is declared (ModSpec defines none). |
| (REQ009) | - | B | **Removed, no requirement.** See the NOTE above. The summary table skips from REQ008 to REQ010. | HTML §9.3 "Each schematron pattern is in one schematron element", Reference `<<req-09>>`, which no longer exists (renders as literal "req-09"). Test text: "Each sch:pattern element shall be contained within one sch:schema element." | The test is orphaned. |
| REQ010 `/req/part3/xml/fpi-attribute-is-uri` | R | B | "The value of the sch:schema/@fpi attribute SHALL be a URI that identifies this implementation." | HTML §9.4 "Each schematron @fpi attribute is used only once"; `<<req-10>>`. **Test text is REQ012's statement, not REQ010's:** "The value of the sch:schema/@fpi attribute shall be used on only one Schematron schema." So the "is a URI" statement has no matching test. | MODEL (URI syntax of `@fpi`); the wording "identifies this implementation" is HUMAN. |
| REQ011 `/req/part3/xml/see-attribute-is-identifier` | R | B | "The value of the sch:schema/@see attribute SHALL be the identifier for the requirements class that contains the requirement(s) implemented by the schema" (no final full stop) | HTML §9.5 "Each schematron @see attribute is used only once"; `<<req-11>>`. The heading ("used only once") does not match the requirement text. | MODEL, cross-referenced to requirements-class identifiers in the records. |
| REQ012 `/req/part3/xml/one-fpi-attribute-per-schema` | R | B | "The value of the sch:schema/@fpi attribute SHALL be used on only one Schematron schema." | HTML §9.6 "Each schematron fpi attribute is used only once"; `<<req-12>>` | MODEL: uniqueness across all Schematron files of the standard. |
| REQ013 `/req/part3/xml/first-pass-core-conformance` | R | C | "A standard passing the XML meta-schema conformance test class SHALL first pass the ModSpec Core conformance test class." | HTML §10.1 "Supports the Specification class"; `<<req-13>>` | MECHANICAL\* |
| REQ014 `/req/part3/xml/pass-XML-schema-conformance-class` | R | C | "A standard passing the XML meta-schema conformance test class SHALL require that its targets (XML schema) pass the XML schema conformance class." (In the adoc the identifier line has no `+` line break, so in XML and HTML the identifier runs directly into the sentence: `...pass-XML-schema-conformance-class A standard passing...`.) | HTML §10.2 "Each XML schema is conformant with the XML Schema class"; `<<req-14>>` | HUMAN: judging whether the target's requirements demand that its targets pass class A. |

### 2.4 Unlabelled normative prose in Part 3 (no identifier in source)

| Location | Verbatim | Apparent kind | Classification |
|---|---|---|---|
| `06-req-class.adoc` lines 180-183 | "In summary, effective modularization is enabled by following the pattern of one conformance class per XML namespace; i.e., the set of components in an XML namespace should be referred to as a whole. Subsetting of components in a single XML namespace for conformance purposes is not permitted." | prohibition ("is not permitted") and a SHOULD; outside any record | MODEL |
| lines 72-78 | "When a process loads a schema as defined by its namespace URI identity, it must always get a linkage to all components in that namespace." and "...when a schema-aware process first encounters a namespace URI it must always be associated to a schema location (a file) that contains or includes all schema components having the URI as their namespace. This is referred to as the "all-components schema document"." | "must" statements that define the central term | MODEL |
| lines 40, 279 | "the extension relationship of this conformance test class to the core must be made explicit." | "must" | MECHANICAL\* |
| line 210 | "First the schema must be defined within the bounds of the XML schema requirements class." | "must"; the only statement of the B-to-A dependency | HUMAN |
| lines 104 and 117 | "The mechanism for dependencies may either be by importation or by inclusion of schema components." and "Either of the above approaches may be used." | permissions in prose | n/a |
| NOTE after PER001 | "A namespace variable is used if the requirements class is not defining a schema, but defining requirements for a schema to be the target of its conformance class. For example, GML defines requirements for application schemas, but does not a priori know the namespace of any application schema. The namespace for the application schema becomes a variable in the conformance test cases." | informative, but it shapes how REQ003 applies to a standard that defines requirements for other people's schemas | HUMAN |

---

## 3. What Parts 2/3 change or add for a checker of Part 1 requirement records

1. **There are no records to find.** Compiled XML of Part 1 (`08-131r7.xml`) has 113 `<requirement>`, 8 `<permission>` and 5 `<recommendation>` elements. Compiled XML of Part 2 and of Part 3 has **zero** `<requirement>`, `<permission>`, `<recommendation>`, `<requirements_class>`, `<conformance_class>`, `<abstract_test>` or `<annex>` elements (grep). The adoc has `[requirement,model=ogc,type="general"]` and `[permission,model=ogc,type="general"]` attribute lines, but the content is a table, so each provision compiles to `<table anchor="req-NN">` or `<table anchor="per-NN">`. A checker that reads only Metanorma XML will see nothing in Parts 2/3. A checker that must handle them needs a table-shape parser: row 1 is the bold label (REQ###) plus the bold identifier URI path, then the text; rows `A` and `B` hold sub-parts; a `<note>` can be nested inside the `<table>` after `<tbody>` (REQ003 in Part 2; REQ005 and REQ008 in Part 3).
2. **Two identifier systems.** Parts 2/3 pair a label `REQ001`/`PER001` (unique only within the document; Part 3 skips REQ009) with an identifier path (`/req/part2/uml/...`, `/per/part3/xml/...`). Part 1 records carry only the path. Part 1's own text (`05-conventions.adoc` "Finding requirements and recommendations") still speaks of labels such as REQ001, REC001, PER001.
3. **Identifier shape.** Paths are `/req/<part-tag>/<tech>/<slug>` (`part2/uml`, `part3/xml`), unlike Part 1's `/req/core/<slug>`. The relative-to-namespace rule is stated for `modspec-2/1.1/` and `modspec-3/1.1/`. Part 1's `modspec-1/1.1/` is written with the Metanorma macro `identifier:[...]`. Parts 2/3 write the namespaces as plain text or links, so macro-based extraction does not see them. The convention text says that using "req" "denotes https://www.opengis.net/spec/modspec-2/1.1/", with no `/req/` segment. Part 1 class identifiers use `.../req/req-class-core`, so the rule is ambiguous (5.21).
4. **Identifier hygiene is not guaranteed.** Required checks for the source form: slug characters (P3 REQ005 contains a space; P3 REQ014 has uppercase "XML"); label/identifier agreement between the summary table and the body (P2 REQ004, P2 REQ007, P3 REQ005); identifier line terminated before the text (P3 REQ014).
5. **Requirements-class identification is broken.** All three class tables use `/req/core/data-representation` as their identifier row, which is outside the Part 2/3 namespaces and not defined in Part 1 (grep finds it only in these three tables). Class C has no table. So the rule "each requirement's identifier prefix matches its class" cannot be evaluated, and the rule that every class has an identifier, a target type and a dependency list fails for class C. The "Target" row is the only target-type information and it is not a `target-type::` field.
6. **Dependencies are document citations.** "OGC ModSpec Version 1.1 [OGC 25-003r1]" (P2) and "[25-003r1]" (P3, class A) cite 25-003, which Part 1's foreword identifies as the "ModSpec Version 1.1 Release Notes [OGC 25-003]" (`$CLONE/sections/00-foreword.adoc` line 10; release-notes docnumber is 25-003r3). Part 1 itself is 08-131r7. Part 1 REQ22 (`/req/core/req-class-not-core-stt-subtype-of-core`) requires "the core as a direct dependency" and a subtype target type; the Parts do not name the Core class or state the subtype relation of "ModSpec Conformant UML/XML Model" to "Standard".
7. **Tests have no identifiers and no `target::`.** Part 1's pattern is `[abstract_test]` with `identifier:: /conf/core/...` and `target:: /req/core/...`. Parts 2/3 use unnumbered subclauses with four numbered list lines (Test Purpose, Test Method, Reference, Test Type). The only link to a requirement is `Reference: <<req-NN>>`, which the HTML renders as "Table N" (for example P3 REQ006 is "Table 8"). A checker needs: test-to-requirement 1:1 by xref; the test text must equal the requirement text (fails for P3 REQ006, REQ008-A, REQ010); the xref target must exist (fails for `req-09`).
8. **Test clauses are not an annex.** The test suites are plain `==` sections, not `[appendix,obligation=normative]` as in Part 1 (`aa-abstract-conformance.adoc`: `[[annex-A]] [appendix,obligation=normative]`). `<<annex-A>>` is therefore undefined; the sections have anchors `annex-A-1` (to `-3` in P3).
9. **Modal verbs.** Use of case: `_SHALL_` is the norm, but P2 REQ005 has lowercase "shall", P3 REQ005 and REQ007 contain a second lowercase "shall" in the same sentence, and P3 PER002 has lowercase "may". Search must be case-insensitive.
10. **Multi-part requirements** are rows labelled `A` and `B` in a table (P2 REQ008, P3 REQ008), not repeated `part::` lines. In P2 REQ008 A and B are alternatives ("...SHALL be equal or" / "...SHALL be an extension"), which conflicts with Part 1 REQ1's "Failure to pass any part of a requirement SHALL be a failure to pass the associated conformance test" (`/req/core/reqs-are-testable`).
11. **Every clause compiles with `obligation="normative"`** (including Scope, Conventions and the clauses full of informative "will" statements), except the Normative references. So "informative vs normative" cannot be told from the XML. Part 2/3 §7.1 defines the convention ("In informative sections, the use of the word "will" implies that something is an implication of a requirement") but nothing in the markup marks a section informative.
12. **Boilerplate replaces authored text.** Both Parts' `03-norm-refs.adoc` begin "While the ModSpec Part 1 Standard references UML and its technical specification, no requirements are derived from these documents." That paragraph is absent from the compiled XML and HTML (grep: 0 hits in both). The XML instead has the Metanorma boilerplate "The following documents are referred to in the text in such a way that some or all of their content constitutes requirements of this document." The two statements are opposite (5.12).
13. **Modifications required of the Part 1 tests.** Part 1's `/conf/core/...` list includes `/conf/core/req-in-only-one-req-class` and omits a test for `/req/core/conf-class-test-req-class`; Part 1 sources also contain two files with the same requirement identifier (`REQ1_reqs-are-in-class.adoc` and `REQ028_reqs-are-in-class.adoc`, both `/req/core/reqs-are-in-class`). I noticed these in passing; I did not verify how they compile and did not digest Part 1.
14. **Mapping from packages to requirements classes.** Part 2 says "associated" (REQ004, REQ005, REQ006) and "the mapping from parts of the model to the requirements classes" but defines no notation, tag, stereotype, naming rule or record field. Neither does any Part 1 record type. A checker for REQ004 to REQ011 therefore has no input defined by ModSpec. The gap is in ModSpec; a project convention would be needed, and I do not propose field names here.
15. **Schema annotations.** The only schema-level annotation duties are P3 REQ004 (`schema/annotation/appinfo` carries the URI of the associated conformance test class, in the all-components schema document), and for Schematron `@fpi` (REQ010, REQ012) and `@see` (REQ011). No other documentation element is required by either Part.

---

## 4. Relevance to a standard that defines a modeling language

### 4.1 What the Parts govern

- Part 2 governs the standard's **own** data/object model. In the text, "the organizing mechanism for the data model used in a standard" is mapped to requirements classes. For a modeling-language standard this is the **metamodel** (abstract syntax) that the standard itself publishes in UML. It does not govern the models that users later write in the language. The text does not distinguish a standard about a domain model from a standard that defines a language, so applying it to a metamodel is my reading.
- Part 3 governs a standard "which has as one of its purposes the introduction of a new XML schema". An XML encoding of such a standard defined as XSD falls inside class A. Class B applies only if Schematron is used. Class C (REQ013, REQ014) covers a standard that introduces "a new type of XML schema" ("Such a standard would normally define the characteristics of such schema, how its components are created and its intended uses"). It matches a standard that defines rules for building XML schemas for domain models (the GML application-schema pattern) and would then require those schemas to pass class A. Whether a given standard is of that kind depends on its content; I am interpreting.
- **Part 2 has no counterpart of Part 3's meta-schema class.** Nothing in Part 2 covers a standard that defines how others build UML models.
- **JSON has no Part.** Part 1 lists only future Parts: scope "Future Parts to the ModSpec Standard may include: Part 4: RDF/OWL requirements; and Part 5: JSON Schema." (`01-scope.adoc`); Part 1 preface "Planned extensions include: ... ModSpec Part providing requirements and recommendations for specifying requirements and conformance tests using JSON." Part 1 clause 9 (`07-mapping.adoc`, anchor `cls-9`) says: "Standards that take an alternative mechanism to the ones defined in the additional Parts must be tested solely on the structure of their conformance test suite until such times as an extension to the ModSpec is defined for that alternate mechanism." So a JSON encoding is not governed by Parts 2/3. Under that sentence it is judged only on test-suite structure.

### 4.2 Provisions that are prescriptive about the **form** of the model

Part 2 (all on the standard's own model):
- UML (or a UML mapping) must be the core mechanism or a normative adjunct (REQ002).
- An explicit package dependency graph, consistent with classifier usage, including external packages (REQ003).
- Every class lives in a leaf package (REQ011). A leaf package contains only classes (the prose definition), and "a class and its contained local classes" count as one package.
- Each leaf package belongs to exactly one requirements class (REQ004). Each requirements class is associated to "a unique package" and to "some number of complete leaf packages and all classes and constraints in those packages" (REQ005, REQ006). The bold, unlabelled recommendation says one requirements class should map to one UML package.
- Classes common to all requirements classes sit in a package associated to the core class (REQ007).
- Package dependency must be reflected as "equal or extension" of requirements classes (REQ008, REQ009), and co-dependent packages share a class (REQ010).
- Not prescribed: UML version ("The terminology used here is common to all versions of the UML standard, and may be applied to any such version."), serialization (XMI or other), diagram form, stereotypes, naming, documentation elements.

Part 3 (the XML schema):
- One XML namespace per requirements/conformance class (REQ003 and the unlabelled "one conformance class per XML namespace").
- One "all-components schema document" per namespace that states the conformance class URI in `schema/annotation/appinfo` (REQ004). It may be assembled by `include` (PER001).
- Schema imports must mirror requirements-class dependencies, and `schemaLocation` must refer to the all-components document (REQ005 and its NOTE).
- Extensions may restrict only optional elements and may specialize types (PER002).
- Schematron: `@fpi` is a URI and unique; `@see` is the requirements-class identifier; each assert or pattern implements at most one requirement (REQ008, REQ010 to REQ012).

### 4.3 Practical consequences for a metamodel (my inference, flagged as such)

- REQ010 together with Part 1 REQ16 merges co-dependent packages and requirements classes. A UML-like metamodel normally has mutually dependent packages. Such a metamodel would collapse into one requirements class unless its packages are layered acyclically.
- REQ011 forbids classes in a package that also has subpackages. That excludes the common pattern of a root package holding a few shared classifiers beside subpackages.
- Part 1 defines a leaf package as one that "contains classifiers" (`definitions.adoc`/`04-terms-and-defs.adoc`: "UML model package that does not contain any subpackages, but contains classifiers [UML]"), while REQ011 and the Part 2 prose say "classes". It is unclear whether enumerations, data types, interfaces and association classes must also be in leaf packages and in the class-association scheme.
- REQ002 asks for UML itself or a normative UML adjunct. A "UML-like" language that is not UML needs the mapping the Part permits in prose ("other object modeling languages and, if needed, the object code itself can be mapped to a UML model"). Whether a UML profile counts as UML is not addressed.

### 4.4 Mandatory or optional?

The sources point both ways. I quote them and do not resolve it.

- Parts call themselves optional. P2 Foreword: "This Part 2 specifies the optional UML Requirements Class." P2 §7.2 title: "Optional Requirements class: UML model extension to the core." P3 Foreword: "This Part 3 specifies the optional XML Requirements Class." P3 §7.1.2 and §7.1.3 titles begin "Optional Requirements class". P3 §7.1.1 ("Requirements class: The XML schema extension to the core") does not use the word "Optional" in its title.
- Parts are conditional. P2 §7.2: "If the organizing mechanism for the data model used in the standard is an object model, then the mapping from parts of the model to the requirements classes should follow the logical mechanism described here." (SHOULD, conditional). Part 3 scope: applies to "any standard which has as one of its purposes the introduction of a new XML schema".
- Part 1 `cls-9`: "Additional Parts to the ModSpec define a mechanism to map parts of the model (language, schema, etc.) to the conformance classes used in the ModSpec model". Part 1 `cls-2`: "Part 1: Core of the ModSpec (this document) defines one requirements class and one related conformance class" and the other Parts are "additional Parts (volumes)".
- Part 1 `01-scope.adoc` NOTE: "the ModSpec is written to be non-OGC specific and can be used by any Standards Development Organization (SDO) as a formal guide for structuring a standards document."
- Policy (OGC 25-001, `document.adoc`: `:status: Draft`, `:issued-date: 2026-xx-xx`, `:edition: 1.1.0`, so not yet in force by its own metadata), `06-policy.adoc` line 9: "Any new OGC Standard, revision to an existing OGC Standard, new abstract specification that has requirements, or revision to an existing abstract specification that has requirements SHALL comply with the requirements stated in the OGC ModSpec Core Standard and relevant Parts." The word "relevant" is not defined. The Policy's scope paragraph on Part 2 reads: "Part 2 of the ModSpec defines the requirements for using UML. The UML extension is if the organizing mechanism for the data model used in a standard is an object model. Then the mapping from parts of the model to the requirements classes should follow the logical mechanism described in Part 1 of the ModSpec." ("Part 1" is an error; see 5.16.)
- Policy exception text: "Failure of a candidate standard to comply with the OGC ModSpec Policy should be specifically noted and reasons given for such non-compliance in the conformance clauses of any new or new version of such candidate standards. The adoption of such documents not compliant with the ModSpec SHALL be considered as an authorized exception to the requirements of the ModSpec. An exception to the ModSpec will require a Technical Committe vote as specified in the OGC's Policy and Procedures." and "A Community Standard may or may not follow the model and requirements as specified in the ModSpec."
- Policy Annex rule: "All OGC Implementation Standards documents SHALL have an Abstract Test Suite (Conformance Test Suite) document in Annex A of the standards document. This Annex SHALL be designated as `normative`" and "Each component of the standard, including requirements, requirements packages, requirements classes, conformance test, conformance packages, and conformance test classes SHALL be assigned a unique URI." Parts 2/3 themselves put no tests in a normative Annex A and give no URIs to tests or classes (5.4, 5.25).

Net reading: the Parts are optional classes that a standard claims only when it uses that mechanism; the draft Policy makes the "relevant Parts" binding on OGC standards, so for an OGC-track modeling-language standard a UML metamodel makes Part 2 relevant and an XSD encoding makes Part 3 class A relevant. For a non-OGC standard the Policy does not apply and Part 1's non-OGC note applies. A JSON encoding is not covered.

---

## 5. Contradictions, ambiguities, typos and apparent errors

"P1" is Part 1. Locations are adoc files under `$CLONE/24-06x-*/sections/` unless stated; line numbers may be off by one or two.

**Identifiers, classes and structure**

5.1 Requirements-class identifier. The identifier row of the UML class (P2 `06-req-class.adoc:32`), of class A (P3 `:28`) and of class B (P3 `:200`) is the same: `2+|/req/core/data-representation`. It is outside the Part 2/3 namespaces, it is not defined in P1 (grep over all `.adoc` finds only these three occurrences), and it is the same for three different classes. Class C has no table at all.

5.2 Dependency rows. P2 `:34` "OGC ModSpec Version 1.1 [OGC 25-003r1]"; P3 `:30` "OGC ModSpec Version 1.1 [25-003r1]"; P3 `:202` "OGC ModSpec Version 1.1 (need proper title and document number)". 25-003 is the Release Notes series (P1 `00-foreword.adoc:10` "ModSpec Version 1.1 Release Notes [OGC 25-003]"; `release-notes-1-1/document.adoc` docnumber 25-003r3), whereas P1 is 08-131r7. A document is cited where P1 REQ22 expects "the core as a direct dependency".

5.3 Identifier variants within one document: P2 REQ004 body `/req/part2/uml/leaf-model` versus summary table `/req/part2/uml/leaf-package`; P2 REQ007 body `/req/part2/uml/common-req-classe` versus table `/req/part2/uml/common-req-classes`; P3 REQ005 body `/req/part3/xml/direct dependency` (contains a space) versus table `/req/part3/xml/direct-dependency`; P3 REQ014 identifier line has no line break, so identifier and text run together in XML and HTML.

5.4 Tests are not identified. There is no `/conf/` identifier for any test or conformance class in P2 or P3, although 6.2 says "All conformance tests that appear in this document are denoted by partial URIs which are relative to the namespace shown above." and the Policy says each "conformance test, conformance packages, and conformance test classes SHALL be assigned a unique URI".

5.5 P3 numbering gap. The Schematron summary table runs REQ007, REQ008, REQ010, REQ011, REQ012. The body NOTE says "Requirement 9 was removed in the ModSpec version 1.1 as this requirement is present in the latest Schematron RelaxNG schema." Its test remains (HTML §9.3, "Each schematron pattern is in one schematron element", Reference `<<req-09>>`, test text "Each sch:pattern element shall be contained within one sch:schema element."). The anchor `req-09` no longer exists and the HTML shows the literal "req-09".

5.6 P3 `02-conformance.adoc`: "There are two conformance classes in this document for:" but there are three requirements classes and three test classes (anchors `annex-A-1`, `annex-A-2`, `annex-A-3`). The third, "Conformance Class: XML meta-schema", is not listed in clause 2.

**Cross-references to Part 1 and inside the Parts**

5.7 Cross-references that are wrong or do not resolve.
- P2 and P3 `01-scope.adoc` (line 19 / 21): "As suggested in Clause Requirement 8 of the ModSpec Core, the structure of the normative clauses in a standard should parallel the structure of the conformance test classes in that standard." P1 `07-mapping.adoc:19` says "As suggested in Clause <<req-22>>, ..." for the same sentence. In P1, `req-8` is `/req/core/requirements-class-correspondence-to-conformance-classes` (one-to-one correspondence); `req-22` is `/req/core/req-class-not-core-stt-subtype-of-core`; the parallel-structure statement is `/rec/core/parallel-structure` (REC002: "If possible, the structure of the normative clauses of the standard SHOULD parallel the structure of the conformance classes in the conformance clause."). Three documents point to three different places.
- P2 `06-req-class.adoc:150-153`: "By Clause <<req-22>> in the Core, only classes in the source requirements class will be affected by the requirement." P1 `req-22` does not say this. The anchor `req-22` does not exist in P2, so the xref is dangling (HTML shows literal "req-22").
- P2 §7.1: "See the formal definition of requirement in <<term-requirement>>". No such anchor in P2; P1's anchor is `requirement-definition`. Dangling (literal "term-requirement" in HTML).
- P2 `02-conformance.adoc`: "The various subclauses of <<cls-6>> list requirements ... This requirements class is an extension of the Core presented in the ModSpec Core Standard <<cls-6>>." Both xrefs resolve to P2's own clause (HTML "Clause 7" both times), so the second points at the wrong document. P3 has the same two-way use of `<<cls-6>>`.

**Wording and logic inside Part 2**

5.8 P2 REQ008: parts A and B are joined by "or": A "...their requirements class SHALL be equal or", B "The source package's class SHALL be an extension of the target package's class." This makes them alternatives and conflicts with P1 REQ1 (`/req/core/reqs-are-testable`): "Failure to pass any part of a requirement SHALL be a failure to pass the associated conformance test." "equal" is not defined (equal requirements classes?). REQ008 and REQ009 say nearly the same thing at package level and leaf-package level.

5.9 P2 REQ005: uses lowercase "shall" (a checker keyed on `SHALL` misses it). "associated to a unique package" is ambiguous (a package unique to the class, or exactly one package). REQ006 says a class is associated to "some number of complete leaf packages". The bold, unlabelled sentence after REQ008 says a requirements class "should be associated to one and only one UML package", weaker than REQ005's "shall".

5.10 P2 `06-req-class.adoc:202-203`: "Although there is nothing to demand it, it is a common practice to move all classes down the hierarchy to leaf packages." This lead-in is immediately followed by REQ011: "The UML model SHALL segregate all classes into leaf packages." The text says nothing demands it, and then a requirement does.

5.11 P2 says "classes" (REQ011: "all classes"; prose: "Leaf packages are those that contain only classes"), while P1 defines "UML model package that does not contain any subpackages, but contains classifiers" (`04-terms-and-defs.adoc`/`definitions.adoc`, term LeafPackage). Enumerations, data types, interfaces and association classes are classifiers but arguably not classes.

5.12 Normative references. Authored text in both Parts: "While the ModSpec Part 1 Standard references UML and its technical specification, no requirements are derived from these documents." That paragraph is absent from the compiled XML and HTML (grep: 0 hits). The compiled output has the Metanorma boilerplate "The following documents are referred to in the text in such a way that some or all of their content constitutes requirements of this document." The two statements are opposite, and the compiled one is what readers see.

**Wording and logic inside Part 3**

5.13 P3 requirement/test mismatches.
- REQ006 `no-element-modification` has exactly the text of REQ004: "The all-components schema document for an XML Schema SHALL indicate the URI of the associated conformance test class in the schema/annotation/appinfo element." Its test (HTML §8.6) states a different rule: "No requirements class in a standard conformant to the XML schema conformance class shall modify elements, types or any other requirement from a namespace to which it is not associated." This also conflicts with §6.4's "stated in one and only one place".
- REQ008 A says "Each sch:assert element SHALL implement constraints described in no more than one requirement."; its test (HTML §9.2) says "Each sch:pattern element shall implement constraints described in no more than one requirement. Each requirement shall be implemented by no more than one sch:pattern." Which element is meant is unclear.
- The test that cites `<<req-10>>` (HTML §9.4, heading "Each schematron @fpi attribute is used only once") carries REQ012's text, "The value of the sch:schema/@fpi attribute shall be used on only one Schematron schema.", while REQ010 says "SHALL be a URI that identifies this implementation". REQ010 therefore has no matching test. HTML §9.6 (Reference `<<req-12>>`) repeats the same text.
- HTML §9.5 has the heading "Each schematron @see attribute is used only once" but REQ011 says "SHALL be the identifier for the requirements class that contains the requirement(s) implemented by the schema".

5.14 P3 PER002 ("Requirements may add constraints." with "restrict ... Usage of existing elements, but only if their use was originally optional") sits uneasily with P1 REQ18 ("No requirements class SHALL redefine the requirements of its dependencies, unless that redefinition is for an entity derived from but not contained in those dependencies.") and with the §8.6 test text. They are not necessarily contradictory (restriction versus redefinition), but this is not reconciled. PER002 also uses lowercase "may".

5.15 P3 target types. The "Target" row says "ModSpec Conformant XML Model" for A and B, but the provisions' subjects differ: "An implementation" (REQ001, REQ002), "a standard conformant to the XML schema conformance class" (REQ003, REQ005), "The all-components schema document" (REQ004), "A standard passing the Schematron conformance test class" (REQ007), "A standard passing the XML meta-schema conformance test class" (REQ013, REQ014). P1 REQ4 requires "a single standardization target type" per requirements class and REQ5 the same per conformance test class. P2's target is likewise "ModSpec Conformant UML Model" while REQ001 speaks of "An implementation".

5.16 Part numbering is off by one in other documents. The Policy (`06-policy.adoc`, scope): "Part 2 of the ModSpec defines the requirements for using UML. ... the logical mechanism described in Part 1 of the ModSpec." The release notes (`release-notes-1-1/sections/clause-1-intro.adoc`): "Part 1 of the ModSpec defines the requirements for using UML ... Part 2 of the ModSpec defines the requirements for using XML." P2 and P3 themselves are consistent with Part 2 = UML, Part 3 = XML.

5.17 Definition of requirement: P2 §7.1 "atomic testable criterion"; P3 §7.1 "an testable criterion" ("an" typo, "atomic" dropped). P1 defines a requirement as an "expression ... that conveys objectively verifiable criteria to be fulfilled and from which no deviation is permitted" (no "atomic").

5.18 §6.4 in both Parts: "The reference to the requirement in the test case is done by a requirements label Recommendations are not tested although they still are documented using a standard template and have unique identifiers." (two sentences merged). P1 says "Recommendations and permissions are not tested". §6.4 also names "REC001, or PER001" as examples, though P2 has no REC and no PER, and P3 has no REC.

5.19 P3 REQ002 "SHALL first pass the W3C Recommendation for XML schema": a Recommendation is not something one passes. The normative references are XML Schema Part 1 and Part 2, second editions of 2004 (XSD 1.0), so XSD 1.1 is not covered, and the Schematron reference is just "ISO/IEC 19757-3:2006".

5.20 P3 REQ004 requires "the URI of the associated conformance test class" in `appinfo`; the test heading says "A reference to the URI of the test suite in AppInfo". Neither Part defines a URI for a conformance class (5.4), so the URI to put there is not determined by Part 3.

5.21 Identifier convention text, §6.2 of both Parts: "For the sake of brevity, the use of “req” in a requirement URI denotes: https://www.opengis.net/spec/modspec-2/1.1/" (and the same for "conf"). Taken literally, `/req/part2/uml/object-model` would resolve without a `req` segment. The examples given ("/req/core/crs" in P2, "/req/part3/xml" in P3) are not provisions of these documents. P1 has the same wording (with the `identifier:[...]` macro).

5.22 P3 §7.1.1 Example: "In GML 3, the spatial schema (ISO 19107) and the general feature model (ISO 19109) are both satisfied by elements within the single GML namespace. A viable alternative would to have put the schema components for spatial schema and feature schema in separate namespaces." ("would to have", missing "be".) If the two models are separate requirements classes, one namespace holds two classes, contradicting REQ003 and "one conformance class per XML namespace".

5.23 Mentions of the wrong Part inside P3: clause heading "Requirements Class: Part 2: XML" (`06-req-class.adoc:2`); "In the ModSpec Part 2 extension, this identifier is a URI." (line 237, REQ010) and "In the ModSpec Part 2 extension, this attribute is the identifier for a requirements class." (line 249, REQ011). P3 is Part 3.

**Document structure, metadata, tooling**

5.24 Metadata. `:docsubtype: logical-model` (adoc) versus `<subdoctype>implementation</subdoctype>` (XML) and "Document subtype: Implementation" (HTML). External identifier uses `doc/POL/...` while HTML says "OGC Standard". `:draft: 3.0` and `<revision-date>##</revision-date>` appear on an approved document. P3 lists "Submitting Organizations" twice (HTML IV and VIII) with different names ("ImageMatters/Tema" versus "Tepa Enterprise Solutions (ImageMatters)"; the Danish Agency for Climate Data absent from VIII). The standalone `https://docs.ogc.org/pol/24-066r1/24-066r1.html` has the keyword "oogcdoc".

5.25 Test clauses are not an annex. Both Parts write `<<annex-A>>` ("The test suite is in <<annex-A>>"), which is not defined. The tests are ordinary `==` sections (anchors `annex-A-1` etc.), numbered as clauses 8 (P2) and 8 to 10 (P3) in the HTML, and in the XML they are `<clause>` inside `<sections>`, not `<annex>`. P1 uses `[appendix,obligation=normative]`, and the Policy says the test suite is in "Annex A ... designated as `normative`". HTML clause numbering also skips 5 (Terms = 4, Conventions = 6, Requirements Class = 7), so anchor `cls-5-3` displays as 6.4 and the cross-reference to `cls-6` displays as "Clause 7".

5.26 Every test reads "Test Method: Inspect the document to verify the above." including tests whose object is a UML model, an XSD or a Schematron file, not a document.

5.27 The word "Optional" in headings is used inconsistently: P2 §7.2 "Optional Requirements class: UML model extension to the core"; P3 §7.1.1 "Requirements class: The XML schema extension to the core" (no "Optional"); P3 §7.1.2 and §7.1.3 begin "Optional Requirements class". Foreword of each Part calls the class "optional".

5.28 P1 REQ14 asks that "corresponding requirements classes and conformance test classes" have "similar names". P2: "UML extension to the core" versus "UML model extends The Standard". P3: "XML Schematron extension to the core" versus "Schematron".

5.29 Smaller points. P2 §6.1 symbols: "UML 2 ... accepted as a publicly available standard (PAS) by ISO in its earlier 1.3 version" (inherited from P1; a UML 2 claim tied to "1.3"). P2/P3 preface cite "Subclause 5.3 of [OGC 05-008]" for terms, whereas P1 cites "OGC Policy Directive 49" and the release notes cite "OGC06-121r9". Foreword text "The ModSpec specifies a formal structure ... does not supply specific content" is identical in both Parts apart from the one sentence naming the Part.

---

## 6. What I could not read or understand

- I did not read the PDFs (`24-065r1.pdf`, `24-066r1.pdf`, `08-131r7.pdf`, `08-131r3.pdf`). I relied on the AsciiDoc, the compiled XML and the HTML, which agree with each other.
- I did not read the referenced external documents: OMG UML 2.5 and 2.4.1, W3C XML Schema Part 1 and Part 2, ISO/IEC 19757-3:2006 (Schematron), OGC 05-008, OGC Policy Directive 49, OGC 06-121r9, the ModSpec Release Notes 25-003r1 as a published document. The version in `$CLONE/release-notes-1-1/` is 25-003r3. I therefore could not verify that `@fpi` and `@see` are attributes of `sch:schema` in ISO 19757-3, or what "Schematron RelaxNG schema" means in the REQ009 NOTE.
- I did not open the images (`$CLONE/images/*`, `$CLONE/models/ogc-modspec.lutaml`) or Part 1's UML Annex C diagram. Whether Annex C's model covers Parts 2/3 concepts (leaf package, source/target package) is unknown.
- I did not re-digest Part 1. My Part 1 statements are limited to the sources cited.
- I could not tell what "relevant Parts" means in the Policy, what "equal" means in P2 REQ008, what "unique package" means in P2 REQ005, whether the third class in P3 is intended to be named in clause 2, or which requirement P3 REQ006 is meant to state (the test suggests a no-modification rule).
- I could not tell how a requirements class is meant to be "associated" to a UML package in any machine-readable way (3.14), or what identifier a Part 2/3 requirements class or conformance class is supposed to have.
- I did not check the live OGC Naming Authority site or whether `https://www.opengis.net/spec/modspec-2/1.1/` and `.../modspec-3/1.1/` resolve.

---

## Summary

1. Part 2 (24-065r1) and Part 3 (24-066r1) are edition 1.1, status approved, published 2026-05-21. Each calls itself an "optional" extension of the Part 1 Core (08-131r7).
2. Part 2 has one requirements class and 11 requirements (REQ001 to REQ011); target "ModSpec Conformant UML Model". It governs the standard's own UML model: leaf packages, one requirements class per leaf package, package dependencies mirrored by requirements-class extension.
3. Part 3 has three requirements classes: XML schema (REQ001 to REQ006, PER001, PER002), Schematron (REQ007, 008, 010 to 012) and XML meta-schema (REQ013, REQ014; no class table). REQ009 was removed but its test remains. There are 13 requirements and 2 permissions in all; neither Part has a labelled recommendation.
4. Neither Part has abstract-test identifiers. Tests are unnumbered clauses linked only by `Reference: <<req-NN>>`, and they are not in a normative annex.
5. Compiled XML of both Parts contains no `<requirement>`, `<permission>`, `<requirements_class>` or `<abstract_test>` elements; every provision is a plain table. A checker that reads only Metanorma XML finds nothing in Parts 2/3.
6. All three class tables carry the same identifier row `/req/core/data-representation`, outside the Parts' namespaces and not defined in Part 1; the "Dependency" row cites 25-003r1 (the Release Notes), not the Core class.
7. Identifier defects: P2 REQ004 and REQ007 and P3 REQ005 differ between table and body; P3 REQ005 contains a space.
8. Requirement/test mismatches in Part 3: REQ006 repeats REQ004's text; REQ008-A says `sch:assert` but its test says `sch:pattern`; REQ010 has no matching test (the test cites req-10 but carries REQ012's text); the test for removed REQ009 survives.
9. Part 2 contradicts itself on leaf packages: "nothing to demand it" immediately before REQ011 "SHALL segregate all classes into leaf packages"; P2 REQ008's A and B are alternatives, which conflicts with Part 1 REQ1 ("any part").
10. Both Parts cite Part 1 wrongly or unresolvably ("Clause Requirement 8", `req-22`, `term-requirement`, `annex-A`).
11. The authored normative-references paragraph ("no requirements are derived") is dropped by compilation and replaced by boilerplate saying the content "constitutes requirements".
12. Unlabelled normative prose exists: P2's bold "should be associated to one and only one UML package" (a recommendation with no REC identifier), P3's "Subsetting ... is not permitted", and several "must" statements.
13. Classification: nearly everything is MODEL (UML or XSD inspection, cross-checked with the records). Only the "first pass the Core" dependency declarations (P2 REQ001, P3 REQ001 and REQ013) are MECHANICAL, and only if records carry a dependency field, which Part 1's record examples do not show. P2 REQ002 and P3 REQ014 are HUMAN. PER001 and PER002 are untestable.
14. For a modeling-language standard such as a UML-based metamodel standard: Part 2 applies to the standard's own metamodel, not to user models; REQ010 and REQ011 push towards acyclic, leaf-only package structures. Part 3 class A applies to an XSD encoding; class C resembles "rules for building XML schemas for domain models". No Part covers JSON; Part 1 clause 9 says alternative mechanisms are judged on test-suite structure only.
15. Mandatory or optional: the Parts say "optional" and conditional; the draft Policy 25-001 (status Draft) says standards "SHALL comply with ... Core Standard and relevant Parts", and "relevant" is undefined. Both statements are quoted in 4.4.
16. ModSpec defines no notation for associating packages to requirements classes, and no URI form for conformance classes (needed by P3 REQ004), so a checker for REQ004 to REQ011 and REQ004 (P3) has no input defined by ModSpec.
17. Not read: PDFs, referenced OMG/W3C/ISO documents, 25-003r1, OGC 05-008, images and the Annex C UML diagram.
