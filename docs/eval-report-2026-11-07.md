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
