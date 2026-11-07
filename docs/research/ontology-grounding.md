# Vocabulary grounding: what is pinned, what the template can and cannot do

Prepared 2026-11-07 for plan step 5. Source material is `docs/research/ontology-alignments.md` (read 2026-11-06); this note adds the pins
(`ONTOLOGY-PINS`, values re-checked against the local copies on 2026-11-07) and states the limits. Nothing was loaded into a reasoner and
no ontology file was parsed by a tool for this note.

## What was done

- Pins for BFO-2020, CCO v2.2, NCOR SSN-to-BFO (2017 track, tag v2026-07-18), NCOR PROV-to-BFO (main) and the W3C SSN 2023 draft, in
  `ONTOLOGY-PINS`. Re-check found them all as the research recorded, with one gap: the local SSN-to-BFO clone is shallow and lacks the
  tag's commit, so that commit is taken from the saved GitHub API dump while the release asset's hash was recomputed here and matches.
- No change to the gate, the emitter or any skill. The template has no vocabulary of its own to ground.

## Why nothing more was written

A grounding needs a list of the target standard's terms (for example "sensor", "observation", "system", "plan") and a decision on what
each should be anchored to. The template is target-agnostic by decision, so it has no such list, and inventing one would be exactly the kind
of unrequested content the Architect's rules forbid. The research also found that the sources disagree on core terms (Sensor, Property,
Observation, Sample, System), that the W3C module is a non-normative draft, and that nothing covers software or virtual systems. So there is
no single mapping the template could adopt for a target standard.

## What a target standard has to supply before grounding can start

1. Its term list, with each term's definition as the standard states it.
2. Which SOSA/SSN edition it builds on: 2017 (what Connected Systems cites, and the only edition NCOR maps completely) or 2023.
3. Whether software and virtual systems are in scope (the gap in every source).
4. Whether a mapping is normative or informative. The research recommends informative: explicit, versioned mapping tables that cite
   these sources, because the two SOSA-to-BFO mappings contradict each other.

## Open

- Whether to add a "terms" record kind, or a mapping-table convention, to the record format. This is a design change to the format, so it
  is the owner's decision and was not started.
- Whether any pinned source should be re-read after CCO 3.0 or the W3C draft moves (the draft had 518 commits in 3.5 months).
