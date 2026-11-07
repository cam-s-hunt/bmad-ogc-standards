# Triage Metanorma messages

The outcome is a written reading of every Metanorma message from the last compile (the X010 findings and anything in `.err.html`). The owner decides what to do about each one without opening the compiler log, so each reading says what the message states, which record or clause it concerns, and which of three actions it points to: fix a record, accept it into the baseline, or report it upstream.

## What you cannot infer

- Messages come from the pinned image run offline (`--network none`), so the set is the same on every machine. A different image or an online run gives a different set.
- Several messages fire on clean documents: `MODSPEC_1` on recommendations and permissions, `MODSPEC_2` on an external `inherit`, `OGC_14`.
  Also expected, observed on the pinned image: `MODSPEC_1` on both classes of a **profile** (a requirements class with no requirements:
  "has no corresponding Requirement"; its conformance class with no tests: "has no corresponding Conformance test"); `MODSPEC_2` on a
  conformance class whose external `depends_on` entry compiles to an `inherit::` outside the document. These are what a correct profile or
  an external dependency looks like. They still go into the baseline only by the owner's decision.
- A title with markup that reaches Metanorma as plain text, not through the emitter's `pass:c[...]`, produces `STANDOC_38` and several
  `STANDOC_7` XML-validation messages (observed). From emitted fragments they should not appear; if they do, a title was written by hand. `MODSPEC_1` on a requirement reads identically to the one on an untested recommendation, so check the record before calling it a defect.
- `ogcspec-metanorma/references/observed-behaviour.md` records what was observed per situation; read it before claiming what a message means, and say "not observed" for a message it does not cover.
- Fixing a record is the Architect's job and the owner's decision. Accepting into the baseline and reporting upstream are the owner's alone; give the message text and the evidence, not a recommendation to silence it.

## Hand back

A table of message id, severity, the identifier it concerns, your reading, and the pointed-to action. Name every message you could not explain, and say whether the build had a `doc.xml.abort`, because then there is no document to read.
