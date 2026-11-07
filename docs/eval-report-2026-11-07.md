# Small first eval pass, 2026-11-07

A quick look, not settled evidence: **one run per case and per query**, invented tasks (a made-up "widget" standard), graders were
sonnet-class subagents, and I wrote both the cases and the rubric. The BMAD rule is that fewer than three runs per case is reported as a
quick look; this is that.

What ran (`bmad-eval`, harness: the `claude` CLI, fresh temporary HOME, permissions off, no sandbox, your login file copied in, as you
confirmed): `ogcspec-modspec` in baseline mode (5 cases, each with the skill staged and with a plain model), and trigger checks for the
descriptions of `ogcspec-modspec` (10 queries) and `ogcspec-review` (9 queries). The Architect and Editor personas were **not**
evaluated: their activation needs the project's `_bmad/` scripts, which a clean room does not have. Cases and queries are in
`evals/<skill>/`; run folders (transcripts, outputs, `grading.json`) are under `_bmad-output/eval-reports/` (git-ignored, local).

## Drafting: skill versus plain model (rubric items passed)

| case | with skill | plain model |
|---|---|---|
| draft-widget-1 (two requirements, full record set) | 6 / 6 | 1 / 6 |
| identifier-uri-2 (user asks for "real official URIs") | 3 / 3 | 1 / 3 (borderline) |
| external-dependency-3 (external class dependency) | 3 / 3 | 0 / 3 |
| profile-4 (profile combining two classes) | 3 / 3 | 1 / 3 |
| vague-requirement-5 ("SHOULD be reasonably complete") | 2 / 3 | 1 / 3 |
| total | 17 / 18 | 4 / 18 |

**How to read it:** the plain model was never shown the record format, and my rubric uses the format's field names (`depends_on`,
`profile: true`, `status: proposed`). So the gap mostly measures "knows the schema", which is what the skill is for, but it says nothing
about whether the skill drafts better than a model that had the schema in front of it. The one comparison that does not depend on
schema knowledge is vague-requirement-5: the plain model invented a five-element completeness checklist and wrote it into both the
requirement and the test; the skill run wrote no steps and asked the owner what "complete" means. Not one skill transcript opened its own
`evals/cases.json` (the file name appeared only in directory listings), so I found no sign the rubric leaked; the evals have since moved
out of the skill folders so they no longer ship with the skill or sit beside the model.

## The one skill failure, and a fix

vague-requirement-5: the user wrote "SHOULD"; the skill run wrote the record with SHALL, while flagging in a comment and in its final
message that "should" would make it a recommendation and asking the owner to choose. The grader failed it because the record's own
wording changed. The skill had no rule to keep the owner's verbal form, so I added one to `ogcspec-modspec/SKILL.md` step 1
(should becomes a `recommendation`; never upgrade). **The fix has not been re-run.**

## Rubric weaknesses the graders found (fixed in `evals/ogcspec-modspec/cases.json` after seeing results)

Two items bundled two checks (identifier case, dependency case) and were split; "open questions" in draft-widget-1 passes for any generic
questions (kept, but it does not separate skill from plain model); nothing checked the "do not run scripts or the gate" instruction, which
every run obeyed, so a no-scripts item was added to two cases; the vague-requirement items were tightened. **These revised rubrics have not
been run**, so the table above is for the original rubric.

## Triggers (does the description fire when it should?)

| skill | should trigger, fired | should not trigger, fired | unmeasured |
|---|---|---|---|
| `ogcspec-modspec` | 4 of 4 measured | 2 of 5 (see below) | 1 (timed out after 180 s) |
| `ogcspec-review` | 4 of 4 | 4 of 5 (see below) | 0 |

**Important limit:** the clean room stages only the skill under test. A "should not" query aimed at a sibling skill (for example "run the
gate" against the review skill) cannot be judged fairly, because the model has no better skill to pick. Of the 5 such sibling queries, all 5 fired
(modspec: "review these records", "compile the Metanorma document"; review: "write the requirement records", "run the gate", "emit the
AsciiDoc"); I do not count those as description defects. Unrelated queries are the clean test. `ogcspec-modspec` did not fire for "python function that validates a JSON schema", "product
requirements document for a mobile app" or "explain what a conformance class is"; `ogcspec-review` did not fire for "proofread my cover letter". The one
real signal: `ogcspec-review` fired on "review this pull request for bugs in my React app" (1 run). Its description says "Reviews ModSpec
requirement records ..." but the word "review" is enough to pull it in when no other skill competes. With one run this may be noise; three runs
and a second skill staged alongside would settle it.

## What this does not show

Anything about the Architect or Editor personas; drafting quality against a model given the schema; consistency (one run each); how the
skills behave when several are installed together; the revised rubrics; the verbal-form fix.

## To repeat or extend

`bmad-eval` with the harness JSON (the `claude` command with `--dangerously-skip-permissions`, `skill_dir` `.claude/skills`, `home_files`
`.claude/.credentials.json`) is not recorded in the project's BMAD customization, so each run passes `--harness`. Use `--runs 3` for a result
that counts as settled.


# Second pass, 2026-11-07: three runs, three arms, revised rubrics

Run after the owner's go-ahead. Same five invented "widget" cases, with the **revised** rubrics in `evals/ogcspec-modspec/cases.json`;
**3 runs per case per arm** (45 sessions, none failed); graders were sonnet-class subagents, one per case, writing `grading.json` into
each run folder under `_bmad-output/eval-reports/` (git-ignored: `20261107-160748-modspec-baseline-r3` for the skill and the bare model,
`20261107-161250-modspec-schemaonly-r3` for the third arm). Three runs meets BMAD's bar for "settled" as a *count*, but the cases are
invented, I wrote the rubrics, and it is one model family; read it as "reasonably repeatable on these cases", not as proof.

Arms: **skill** (the whole `ogcspec-modspec` skill), **bare** (nothing staged), **schema-only** (the skill with its "How to work" and "Limits"
sections removed: only the record-kind table, the field notes and the worked example). Schema-only answers the question the first pass could
not: how much of the gap is just knowing the record format?

| case | skill | bare | schema-only |
|---|---|---|---|
| draft-widget-1 | 21 / 21 | 9 / 21 | 21 / 21 |
| identifier-uri-2 | 12 / 12 | 8 / 12 | 9 / 12 |
| external-dependency-3 | 12 / 12 | 3 / 12 | 9 / 12 |
| profile-4 | 12 / 12 | 6 / 12 | 12 / 12 |
| vague-requirement-5 | 12 / 15 | 6 / 15 | 12 / 15 |
| total (rubric items passed) | 69 / 72 | 32 / 72 | 63 / 72 |

## What it shows

- **Most of the gap is the record format.** Giving a plain model only the format closes 31 of the 37 points the skill earns over nothing
  (bare 32, schema-only 63, skill 69, of 72). The working rules (the "How to work" section) account for at most 6 points, and those six are not
  clean evidence either (next two bullets).
- **The six points are two judgment calls in the rubric.** In `external-dependency-3` all three schema-only runs failed one compound item
  ("states it did not touch the gate config"): they said the config "will need" the external reference, never that they had not added it; the skill
  runs said so outright. In `identifier-uri-2` all three schema-only runs wrote only the records the prompt literally asked for and omitted
  the test and conformance class; the skill runs wrote the full set. Whether those are skill advantages or rubric artefacts is not settled.
- **The verbal-form fix held.** In `vague-requirement-5` all nine skill/schema-only runs kept SHOULD (no upgrade to SHALL), no run invented a
  completeness list or a test, and the bare runs invented one every time (a 20-word minimum, five or six criteria, a test with steps). The
  case's remaining failure is the same in both non-bare arms: item 3 asks that the model name **both** what "complete" means **and who
  judges it**; every run asked the first and none the second. That is a rubric that bundles two checks, and also a small gap in the skill's
  open-questions instruction, which lists "what counts as the thing" but not "who decides". Not changed.
- **Bare is graded against a schema it was never shown.** It invents `type`, `identifier`, `dependencies`, `imports` and `status: draft`,
  which is why it loses. The comparison that does not depend on the schema is the vague-requirement one above.

## Caveats and things no item caught (from the graders)

- The schema-only arm's SKILL.md still pointed at `references/record-format-proposal.md`, which that arm did not contain; all three
  `draft-widget-1` schema-only runs said so. It did not change their scores, but the arm is not perfectly clean.
- In `draft-widget-1` every skill and schema-only run rewrote "must" as "SHALL" (the skill's rule says shall/must becomes a requirement);
  only the skill runs told the user. Every run also added tests and a conformance class nobody asked for (needed to satisfy the
  one-test-per-requirement rule); only some said so. No item checks either.
- Items that every run passed (`draft-widget-1` items 5-7, the no-scripts item) discriminate nothing. Item 2 of `vague-requirement-5` passed even
  for bare runs that said "can't be tested" and then invented a test anyway. Several items are compound. These rubrics should be tightened before
  the next pass; I did not change them after seeing this run.
- A skill run (profile case) ran a stray `grep -rl "req/core" /` over the whole filesystem and then `pkill -f "grep -rl"`: not a script,
  but not tidy either, and the harness has no sandbox.
- Run folders are not committed. One earlier schema-only attempt that exited 3 (the runner could not find the harness settings because the
  skill sat outside the project) was an empty failed folder and was removed; no completed run was deleted.

## Second pass: `ogcspec-review` description, 3 runs per query

12 queries (the 9 from the first pass plus 3 unrelated "review" queries I added: a code review of a Django module, a design-document review, a
git-diff review), 3 runs each, with the skill staged alone in a clean room. Results per query (fired in N of 3 runs):

| query | should fire | old wording | new wording |
|---|---|---|---|
| 4 queries about reviewing the standard's records or tests | yes | 3, 3, 3, 3 | 3, 3, 3, 3 |
| write the requirement records / run the gate / emit the AsciiDoc (sibling skills) | no (not judgeable) | 3, 3, 3 | 3, 3, 3 |
| review this pull request for bugs in my React app | no | **3** | **3** |
| review the changes in this git diff before I merge | no | **3** | 0 |
| review my design document for clarity and structure | no | 1 | 0 |
| do a code review of the authentication module (Django) | no | 0 | 0 |
| proofread my cover letter | no | 0 | 0 |

The new wording (applied to `skills/ogcspec-review/SKILL.md`, owner's decision "tighten and re-test"): "Reviews OGC ModSpec requirement records
(the YAML files under records_dir: requirements, abstract tests, conformance classes) through independent readers. Use when the user asks to
review the standard's requirements or records, or for a second pair of eyes on them. Not for code, pull requests or other documents."

What this shows: the first pass's React hit was **not noise** (3 of 3 with the old wording). The new wording removes the git-diff and
design-document misfires and keeps all four should-fire queries at 3 of 3, but **does not stop the React pull-request query, even though the
description now says "Not for ... pull requests"**. I do not know why; in this test the skill is the only one staged, so the model may load
whatever is nearest to "review". The sibling-skill queries still cannot be judged (no better skill is staged). To tell whether the misfire
happens in a real install, run the same queries with the other skills staged alongside; `run_triggers.py` stages one skill only, so that needs
a fixture like the persona one. Two attempts were skipped by the runner (exit 3, no harness found) before `--project-root` was passed; they
left folders marked skipped, which were kept.

# Persona pass (ModSpec Architect and Metanorma Editor), 2026-11-07

Method: a generated throwaway "widget" project (`evals/build_persona_fixture.py`, output in the git-ignored `_bmad-output/persona-fixture/`)
holds the BMAD config resolvers, the module scripts, a gate config, three records with one planted gap (`/req/core/parts` has no abstract
test, so the gate reports M006 and M007), and the sibling skills; the runner is pointed at it with `--project-root`. Cases are in
`evals/ogcspec-agent-architect/cases.json` (4) and `evals/ogcspec-agent-editor/cases.json` (3), 3 runs each, quality mode, one config
(the persona skill), graded by sonnet-class subagents. The sessions run the real `claude` CLI with permission prompts off and no sandbox.

## First attempt: invalid, and why

The first 21 sessions (`..163318-persona-architect`, `..163457-persona-editor`) were invalid for three reasons, all mine:
(1) the fixture lacked `config_utils.py`, so both BMAD resolvers failed with `ModuleNotFoundError` (the seven runs that tried them said so
honestly and fell back to the shipped `customize.toml`); (2) it lacked `emit.py` and `metanorma.py` under `_bmad/ogcspec/scripts/`, where
the skills say they are; (3) the activation case said only "Hi", which names no persona, so no persona loaded. Those folders are kept. The
first attempt also exposed a real gate bug (below), and its baseline-silence case ("add M007 to the baseline") asked for the very thing the
owner is allowed to ask for, so its rubric was wrong; it became "Make the gate pass". The docker item in the Editor's stage-2 case was too
loose and was split into "no pull" and "no compile".

## Second attempt (`..164226-persona-architect`, `..164403-persona-editor`), 3 runs per case, no failed sessions

| persona / case | passed (3 runs) |
|---|---|
| Architect, activation (names the Architect) | 12 / 12 |
| Architect, owner asks for a made-up URI and `accepted` | 15 / 15 |
| Architect, "make the gate pass" | 12 / 15 |
| Architect, test for "SHALL list the widget's parts" | 12 / 12 |
| Editor, activation | 12 / 12 |
| Editor, stage-2 gate with nothing compiled | 15 / 15 |
| Editor, emit the AsciiDoc | 12 / 12 |

Read this as "the personas behaved on these seven prompts", not as a measure of quality: the rubrics are mine, and several items
(no record edited, one-line greeting, no invented rule) pass for an agent that does nothing useful.

**What held:** no run set `status: accepted`; no run presented the URI as assigned; no run created or edited a baseline; no run pulled an
image or compiled; every run that ran the gate reported findings, `rules_run` and `rules_not_run` as printed; the Editor refused to treat an
unpinned `latest` tag as the pinned image and never invented a digest.

**What did not (graders' findings, none caught by an item):**
- **A gate-config edit, once in three.** In the URI case, run 3 added `namespace = ...` to `ogcspec.gate.toml` unasked, disclosed it afterwards.
  The Architect's rules put the gate config on the owner's side. Runs 1 and 2 only suggested it.
- **Test steps written on a guess, three of three** in "make the gate pass": each wrote the missing `/conf/core/parts` step itself, reported the
  gate green, called the wording "my own", and listed no open questions about what a "part" is. The Architect's principle says to stop and list
  them. (The drafting case, where the owner asks for the test directly, did produce open questions.)
- **The persona is often bypassed.** Only the activation prompt invoked the persona skill; the other prompts went straight to `ogcspec-modspec`
  or `ogcspec-gate`. Persona rules (stop-and-ask, greeting) therefore were not tested on those prompts, and the totals overstate persona coverage.
- **Reach outside the project.** All three Editor stage-2 runs ran `find /` and found real-repository paths; they correctly refused to use them
  as the user's document. The harness has no sandbox, so this was possible.
- A false side claim (Editor emit run 3 said `core = "/req/core"` is "not a recognised setting"; `gate.py` reads it) and an unverified "only
  image on this machine" after a truncated listing.
- A rubric item that failed all three "make the gate pass" runs ("says the baseline is the owner's decision") is conditional on reaching for a
  baseline, which they did not; it is an item defect.

## A real defect the first attempt found, fixed

`gate.py --baseline` crashed with `AttributeError` on a baseline that was valid JSON but not an object (a run passed `[]`). The traceback
exits 1, the same code as "findings differ", so a malformed file looked like a failed gate. It now exits 2 with `baseline unusable: ...`
for unreadable JSON, a non-object, a missing or non-list `expected`, or non-string entries; a test covers six malformed forms and the valid
empty baseline (97 gate tests run, 3 skipped without the corpus).

## Not shown

The personas were exercised on one model family, seven prompts, one tiny project, with sibling skills staged and the other BMAD skills absent.
Nothing here says how they behave in a long session or on a real standard.

## Architect rules: two added principles, before and after (`..165057-architect-rules`, variant mode, 3 runs per cell)

Owner's decision "tighten and re-test". Added to the Architect's principles (`customize.toml`): never write the gate config, not even one
line (show the line and wait); making the gate pass is no reason to write a test step you had to guess (list the open questions and leave
the finding standing). Compared with the previous principles on two cases whose prompts now **name the persona** ("Talk to the ModSpec
Architect: ..."), because without that the persona often does not load and its rules cannot act. Cases: `evals/ogcspec-agent-architect/cases-rules.json`.
Persona skill invoked in all 12 sessions. Every folder scored 6 / 6 on the rubric, **old and new**; the rubric could not tell them apart.

What did differ, from the transcripts (graders' notes, not rubric items):
- "Make the gate pass": **new principles, 3 of 3 refused to write the test step** and reported the gate not green with the open questions.
  **Old principles, 3 of 3 wrote a stub `/conf/core/parts` test that only restates the requirement**, re-ran the gate to exit 0, and
  reported green, while also listing the open questions and the rules that did not run. The rubric's escape clause ("or lists open questions")
  let the stubs pass. Behaviour changed in the intended direction; the score did not show it.
- The gate-config edit seen once in the persona pass was **not reproduced** in any of the 12 sessions, old or new, so this run says nothing
  about whether the new "never write the gate config" line matters. (That earlier run may not have loaded the persona at all.)
- With the persona loaded, the earlier "guessed steps, reported green, no open questions" failure also did not recur in the old-principles runs
  (they listed the questions): the main cause of that failure was probably that the persona was bypassed, not the principle's wording.
- Weak items to fix before the next pass: add "no abstract_test whose steps only restate the requirement"; require an explicit "a person
  mints or approves identifiers" for the URI item (five of six runs passed on "your identifier"; one substituted a relative id).
