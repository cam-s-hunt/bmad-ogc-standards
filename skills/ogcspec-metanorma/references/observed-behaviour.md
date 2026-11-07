# Metanorma behaviour observed on the pinned image

Image: Metanorma 2.5.16 (cli 1.18.4, standoc 3.5.11, mn-requirements 0.5.15), OGC flavor, 2026-11-06.
Observed by compiling small OGC documents, not read from code. Re-check after changing the image.

| situation | compiler exit | what appears |
|---|---|---|
| clean document | 0 | still several severity-2 messages (`MODSPEC_1` on recommendations and permissions, `MODSPEC_2` on an external `inherit`, `OGC_14`) |
| requirement with no abstract test | 0 | `MODSPEC_1` on it, identical to the message for an untested recommendation or permission |
| `inherit` to an id that exists nowhere | 0 | `MODSPEC_2`, identical to the message for a legitimate external prerequisite |
| duplicate identifier | 1 | severity-0 `STANDOC_36` / `MODSPEC_3`; `doc.xml.abort` is written and `doc.xml` is not |

Consequences: the exit code cannot be the check; a message cannot be read as a defect without looking at it;
a missing `doc.xml` is a failed build, never "no records". `.err.html` is next to the output and holds each
message's id, severity and the identifier it concerns.

With the container online, a bibliographic reference such as `OGC 99-000` triggers a lookup (`RELATON_4`);
offline it is `STANDOC_40`. The wrapper therefore runs `--network none` by default so message sets compare
across machines.

Compiled semantic XML: a definition is an element with an `anchor` attribute. Its kind is the element name
plus `type` (`requirement` with `class`, `conformanceclass`, `abstracttest`, or no type for a plain
requirement). The anchor-less nested `requirement` elements inside a class are list entries (`general`,
`verification`), not definitions.

Prose is emitted as literal text (`pass:c[...]`). Without that, `*x*`, `_x_`, `` `x` ``, `^x^`, `#x#`,
`<<x>>`, `[[x]]` and bare URLs were changed or dropped by the compile. Metanorma still turns `--` into a
dash and straight quotes into curly ones; the gate normalises those.

## Real documents compiled with this image (offline, 2026-11-06)

ModSpec Part 1, OGC API - Processes Part 1 (v2.0 draft), OGC API - Records Part 1 and OGC API - Connected Systems
Parts 1 and 2 compiled (exit 0, 17-25 s each). OGC API - Features Part 1 (17-069) crashes the compiler (Ruby
NoMethodError in `Metanorma::Utils::LineStatus#process`, metanorma-utils 2.0.11), exit 1 and no XML. Records aborts
(exit 1) when compiled from its own folder because it includes `../../openapi/...`; compiled from the repository
root with `--root` it succeeds. Features writes its requirements as tables, which compile to no requirement
elements, so even a successful compile would give the gate nothing to read (X004).

## Titles, conformance-class dependencies and profiles (2026-11-06, same image, offline)

Observed with `docs/design/step3-compile-tests.py` and `docs/design/record-format-experiment.py`:

| situation | compiler exit | what appears |
|---|---|---|
| `.Core` block title on a requirements class or conformance class | 0 | XML `<title>Core</title>` on the class; no new message |
| the same title with markup written as plain text (`.Core *bold* _x_ <<x>>`) | 0 | the markup is applied (bold, cross-reference lost); `STANDOC_38` and eight `STANDOC_7` XML-validation messages |
| the same title as `.pass:c[Core *bold* _x_ <<x>>]` | 0 | text kept literal; `--` becomes an em dash and quotes are curled; no new message (this is what `emit.py` writes) |
| `inherit::` on a conformance class | 0 | kept: `<inherit>/conf/core</inherit>` in the XML; an external target also gives `MODSPEC_2` on the conformance class |
| a duplicated `inherit::` line | 0 | kept twice in the XML; the gate's X003 reports it |
| a requirements class with no requirements, and its conformance class with no tests (a profile) | 0 | `MODSPEC_1` on each ("has no corresponding Requirement" / "...Conformance test"); both appear in the XML with their `inherit` lists |
