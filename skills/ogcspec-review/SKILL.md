---
name: ogcspec-review
description: 'Reviews OGC ModSpec requirement records (the YAML files under records_dir: requirements, abstract tests, conformance classes) through independent readers. Use when the user asks to review the standard''s requirements or records, or for a second pair of eyes on them. Not for code, pull requests or other documents.'
---
# Review requirement records

The outcome is a findings report on the standard's requirement records that the owner can act on without the drafting conversation. It exists to catch what the gate cannot: a requirement nobody could test as written, a test step that asserts more than its requirement says, a term used but never defined. The review reports and edits nothing.

## Run it

1. Find the gate config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key modules.ogcspec.gate_config_path`. Take `records_dir` from it and review that folder, or the files the user names.
2. Get the owner's own description of the behaviour the records should capture: a document, notes, or a few sentences from the user. Without it the review can judge consistency but not scope, so ask once and say so in the report if none exists.
3. Invoke `bmad-review` with the explicit directive `skill:bmad-review`, the records as the content, the description as context, and the checklist in `references/modspec-checklist.md` as `also_consider`. Give it the records and the description only, never the drafting conversation or the drafter's reasons: a reader that has heard them tends to agree with them.
4. Present its findings as returned, under the heading of the lens that raised each.

## Independence

`bmad-review` runs each lens as a separate subagent that sees only the staged content and the guidance, when subagents are available. Without them it reviews in the current conversation, which has heard the drafting. When you cannot launch subagents, or the review ran in this conversation, open the report with: **NOT INDEPENDENT: reviewed in the drafting conversation.** Never present such a review as a second opinion.

## Limits to state

The review does not replace the owner reading the wording of the normative statements, and it does not check ModSpec Part 1 rules the gate checks; run the gate for those. The adversarial lens requires at least ten findings, so on a small record set some may be weak: say which findings you consider padding.
