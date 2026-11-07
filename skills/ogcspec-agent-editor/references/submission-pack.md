# Submission pack

The outcome is a draft file at `{output_folder}/submission-pack-<date>.md` that the owner, or a human editor they name, reads before anything goes to OGC. The owner acts on it without this conversation, so it must say what is established, what is not, and what only a person can supply. Nothing is sent, posted or filed by you.

## What you cannot infer

- Every identifier appears as a candidate, marked unregistered. You do not assign, register or call one registered, and you do not file with any Naming Authority. OGC may require registered names and a Naming Authority submission; this module has not checked that, so say so and leave the process to the owner.
- Take build facts from a fresh run, not memory: the stage-1 and stage-2 gate output with `rules_not_run`, the compile exit code, and the image digest used. A pack built on stale output misleads the person who relies on it.
- State the limits the owner would otherwise assume away: the gate checks ModSpec Part 1 clause 8 requirements and two draft-Policy rules, not Parts 2 or 3 (its `uml_package` rules, S003 and S004, record a project convention for Part 2 and do not check Part 2); it checks the structure of conformance-class dependencies and profiles (Reqs 12 and 19) but not whether a dependency is used to test, which is for a person; the verbal-form rules follow ISO/IEC Directives Part 2 edition 9.0 as read from a redline copy; the Policy cited is a draft; no test run was performed on the standard's repository CI unless it has run.
- Open decisions belong in the pack: unresolved contested readings, baseline entries awaiting a decision, and any questions the owner has listed for OGC or the ModSpec maintainers.

## Hand back

Where the file is, the three things the owner must check first, and a plain statement that nothing was submitted.
