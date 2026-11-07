# OGC Spec knowledge

This document covers the `ogcspec` module: two agents and several skills that help draft, check and build the requirement records of a standard intended for OGC submission.

## What the module is

The module packages agents, skills and one canonical gate script. It does not enforce anything by itself. The standard's repository CI runs a vendored release of the same gate and is the only blocking check. Agent-side runs are advisory, and so are the agents' stops for the owner: they are instructions, not locks.

## The agents

| agent | Recommend when |
|---|---|
| `ogcspec-agent-architect` (ModSpec Architect) | The user wants to work through requirements across a conversation: drafting records, running the gate, tracing requirements to tests, asking for a review, recording a contested reading of ModSpec as a decision. |
| `ogcspec-agent-editor` (Metanorma Editor) | The user wants the document built: emit, compile a copy, stage-2 gate, an explanation of Metanorma's own messages, or a draft submission pack. It builds and reports; it does not write normative text. |

## The skills

| skill | Recommend when |
|---|---|
| `ogcspec-modspec` | Drafting or revising requirement, class, abstract-test and conformance-class records. |
| `ogcspec-metanorma` | Rendering records to Metanorma AsciiDoc and compiling with a pinned local Docker image. |
| `ogcspec-gate` | Checking records. Prints JSON findings; exit 0 clean, 1 findings, 2 usage error. |
| `ogcspec-review` | The user asks for a second pair of eyes on the records. Independent only when subagents are available; the report says when it was not. |

## Start here

- "Let's write the requirements for X" → the ModSpec Architect.
- "Draft a requirement class for X" → `ogcspec-modspec`, then `ogcspec-gate`.
- "Does this still pass?" → `ogcspec-gate`.
- "Build the document" or "compile it" → the Metanorma Editor, or `ogcspec-metanorma` directly.
- "Review the requirements" → `ogcspec-review`.

## What stays with the owner

An agent drafts; a named human decides. The agents stop for the owner at identifiers and URIs, final normative wording and verbal forms, the gate config and baseline, readings of ModSpec with two answers, and anything sent to OGC. Agents never mint or register OGC identifiers. Commit is left to the standard repository's own rules.

## Where things land

Decision records for contested readings go to `modules.ogcspec.decisions_dir`, set at `bmad setup ogcspec`. The gate config path is `modules.ogcspec.gate_config_path`. The record format is still today's (`ogcspec-modspec`); a proposed template record format is in `ogcspec-modspec/references/record-format-proposal.md` (not accepted, not enforced).

## Dependencies

The module requires the BMad Method module, because the decision-record template and `bmad-walkthrough` come with it, and the review and elicitation skills from core tools.
