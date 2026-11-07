# Personas and workflow: design proposal (2026-11-06)

**Status: decisions made and the skills scaffolded (2026-11-06); see "Decisions made by the owner" at the end and `docs/HANDOFF.md` for what was and was not checked. The text below is the original proposal.** Names, the persona count and the human gates
are the owner's decisions. Plan step 6 asked for this design; the scaffold follows only after a yes.

Every statement is tagged: **read** (a file I opened, named), **inferred** (my reasoning from what I read),
**open** (undecided or unchecked), **stated** (a claim in another document I did not verify).

## Sources and what was not read

BMAD facts come from a clone of the pinned commit `e734d3ac…` (`BMAD-PIN`) made as data in this session's scratchpad.
Nothing from it was run. A separate local copy of BMAD-METHOD is v6.12.4 and was not used.

- **Read in full:** `docs/reference/skills-and-agents.md`, `docs/reference/module-files.md`, `docs/toolsmith/shapes.md`,
  `modules.md`, `agents-with-memory.md`, `modes.md`, `make-a-skill-customizable.md`; `skills/bmad-agent-architect/` (SKILL.md,
  customize.toml, bmod.toml); `skills/bmad-agent-dev/customize.toml`; `skills/bmod-method/roster.toml` (first 40 lines);
  `skills/bmad-review/customize.toml` (first 80 lines); the `prompt` menu items in `skills/bmad-agent-analyst/customize.toml`.
- **Not read:** the bodies of `bmad-review`, `bmad-walkthrough`, `bmad-facilitate`, `bmad-eval`, `bmad-party-mode`;
  `validate_manifests.py`. Where this design relies on them it uses only their descriptions in `skills-and-agents.md`.
- **Not run:** `validate_manifests.py` against any scaffold (none exists yet), any eval, the `npx skills add` route.
- An earlier feasibility note (not in this repository) was read for its section on human
  accountability. Its OGC policy citations are **stated**, not checked here.

## What the pinned BMAD offers for this (read)

- An agent is a skill named `<prefix>-agent-<name>`. Its persona sits in `customize.toml` under `[agent]` (`name`, `title`,
  `icon`, `role`, `identity`, `communication_style`, `principles`, `persistent_facts`, `activation_steps_*`).
  Each `[[agent.menu]]` item has a `code`, a `description` and exactly one of `skill` or `prompt`.
- A `prompt` item is a sentence or two of instruction, for example "Invoke the `bmad-deep-recon` skill with the market research
  type pre-selected". The `prompt` form is the one that fits our scripts.
- A module with an agent needs `roster.toml` in the record folder (`code`, `skill`, `name`, `icon`, `title`, `persona`).
  Each member skill has its own `bmod.toml` with `[skill] bmod` and `source`; `source` must equal the record's `update_source`.
- A memory agent is justified only if "used daily for a month, would the thirtieth session differ from the first?"
- `bmad-review` (body read, `skills/bmad-review/SKILL.md` and `customize.toml`):
  - Lenses are adversarial, edge-case-hunter, verification-gap (code only), structure and prose (docs only). None is ModSpec-specific.
  - **Independence is conditional.** "When subagents are available" it spawns one subagent per lens. Each gets the lens instruction,
    the path of the staged content, `also_consider` and the standing directives, not the calling conversation. Otherwise it
    "run[s] the lenses sequentially yourself", in the same conversation, which is not independent.
  - **Passing ModSpec guidance.** `also_consider` is an ordinary input a caller supplies and reaches every lens. `review_guidance`,
    `persistent_facts` and new lenses are customization: a project override written by `bmad-customize`, which a module cannot ship.
    The body also documents a forwarding caller passing "pre-resolved customization fields", which are honored verbatim for those fields.
  - It refuses uninvited use; "an explicit `skill:bmad-review` directive from another skill counts as that ask".
  - The adversarial lens "requires at least ten concrete findings"; on a small set of records expect padding or re-checks. The skill says
    "zero findings is valid" for the other lenses.
  - It belongs to `bmod-core-tools` (its `bmod.toml`).
- The Method module ships `decision-record` as a `bmad-facilitate` template, per `skills-and-agents.md`.

## Shape test for each candidate persona

A persona earns its place only if a user works with it across turns **and** it owns several related jobs (`shapes.md`).

| candidate | jobs it would own | verdict |
|---|---|---|
| **ModSpec Architect** | draft and revise records (`ogcspec-modspec`); stage-1 gate; trace requirement→test→class; pose and record contested readings; ask for review; run the build chain | **Persona.** Multi-turn, several jobs, and it is where judgement lives. |
| **Metanorma Editor** | emit; compile a copy; stage-2 gate; triage Metanorma messages (X010); draft non-record clauses (scope, terms, references, annexes); prepare a submission pack | **Conditional.** The build chain is mechanical and runs as one action (a menu item). The editorial jobs would justify a persona, but no skill holds know-how for non-record clauses yet. **open** |
| **Reviewer** | read a draft with fresh eyes and report findings | **Not a persona.** A reviewer who has talked to the drafter is no longer independent, so it should be a plain skill whose readers get the records and a checklist, not the drafter's reasons. `bmad-review` does this **only when subagents are available** (see above). `ogcspec-review` must therefore check for subagents and say in its report when it ran without them, i.e. not independently. **inferred** from **read** |
| **Ontologist** (BFO/CCO, SOSA/SSN grounding, plan step 5) | vocabulary alignment | **Not now.** Open decisions (software as material or not; no reasoner run) and no tooling to own. Use `bmad-deep-recon` and `persistent_facts` until step 5 yields a decision. |
| Any memory agent | | **Fails the 30th-session test.** State that must persist (records, decisions, baseline, gate config) belongs in the repository where CI and humans can see it, not in an agent's sanctum. Use `persistent_facts` pointing at those files. |

### Recommendation (superseded: the owner chose Architect + Editor + review; see "Decisions made")

Ship **one persona and one skill first**: the Architect (with a `BUILD` menu item covering the Editor's mechanical chain) and
`ogcspec-review`. Add the Editor persona only when the owner puts non-record clauses in scope for agents and a skill exists for
them. This departs from plan step 6, which names three roles; the reason is that the Editor's only existing content is a chain
of three commands. Alternative: ship both personas now, with the Editor's menu limited to build and submission-pack items.

### Out of scope here (read, by description)

Winston (software architecture), Amelia (code `bmad-build`, TDD, code review), Sally (UX), Mary and `bmad-deep-recon` are
reusable for research only. John and Sofia (briefs, PRDs, ticket tree) are not used; whether Sofia's tickets should hold one
work item per requirements class is **open** and not evaluated. `bmad-party-mode` can seat the Architect beside a human
for a discussion; it was not tried.

## Proposed members

Names are the owner's choice (`[agent].name` and the roster `name` are required by the scaffold).

### `ogcspec-agent-architect` — ModSpec Architect

- **role:** turn the owner's described behaviour into ModSpec requirement records and show what is and is not established.
- **principles (draft):** draft only what was asked; every requirement has one abstract test and one class; write test steps only
  from the requirement text and stop when that needs a guess; identifiers, wording of normative statements and baseline changes
  are proposals until a named human accepts them; report gate findings verbatim; say which checks did not run.
- **activation (inferred, follows `bmad-agent-architect` step 5):** `activation_steps_append` reads
  `modules.ogcspec.gate_config_path` with `resolve_config.py`, then the gate config for `records_dir` and `namespace`.
  `persistent_facts`: `file:` entries for the gate config and the decisions folder (new config question, **open**).
- **menu:**

| code | description | action |
|---|---|---|
| `DR` | Draft or revise records | `skill = "ogcspec-modspec"` |
| `GT` | Stage-1 gate and a plain report of findings | `prompt`: run `ogcspec-gate` stage 1; report `findings`, `rules_run`, `rules_not_run` unaltered |
| `TR` | Trace matrix: requirement → test → class, with the gate's state per row | `prompt`: build it from the records and gate output only; list gaps, do not fill them |
| `RV` | Independent review of the current draft | `skill = "ogcspec-review"` |
| `EL` | Push on a normative statement | `skill = "bmad-advanced-elicitation"`; output is proposals for H2 |
| `DC` | Record a contested reading as a decision | `prompt`: use `bmad-facilitate` `decision-record`; ends at H4 |
| `BUILD` | Emit, compile a copy, stage-2 gate | `prompt`: the loop steps 5–7 below; stops with exit 3 if Docker or the pinned image is missing |

### `ogcspec-review` — plain skill (`[workflow]` customization)

Invokes `bmad-review` with an explicit `skill:bmad-review` directive and the staged records as content. It supplies a ModSpec
checklist through `also_consider`, the route that needs no project override: statements that are not testable as written;
a test step that goes beyond its requirement; verbal form against the kind of record; a requirement whose subject differs
from its class's subject; scope creep against what the owner described; terms used but not defined. It passes the records and
the owner's description of the behaviour, not the drafting conversation. It emits findings only and edits nothing.

Why not `review_guidance` or a ModSpec lens: both are customization, set per project with `bmad-customize`, and forwarding
`review_guidance` as pre-resolved fields would replace whatever the project already set. A project that wants a standing ModSpec
lens can add one itself; the module could document the override in `help.md`. **open**

Which lenses run: `edge-case-hunter` fits requirements that define behaviour; `adversarial` forces at least ten findings;
`structure` and `prose` are editorial and apply to documents, not records. The owner's choice. **open**

### `ogcspec-agent-editor` — included by owner decision (menu limited as described in "Decisions made")

If added: `EM`/`CP`/`G2` as separate items, `X010` triage (read each Metanorma message, never auto-baseline), and a
`SB` item that prepares a submission pack as a draft file and sends nothing.

### Files the scaffold will touch (after approval)

`skills/ogcspec-agent-architect/{SKILL.md,customize.toml,bmod.toml}`, `skills/ogcspec-review/{SKILL.md,customize.toml,bmod.toml}`,
`skills/bmod-ogcspec/roster.toml` (new), `skills/bmod-ogcspec/bmod.toml` (`skills` list; possibly `decisions_dir` question),
`skills/bmod-ogcspec/help/help.md`.

**Dependencies this adds (read in `modules.md`: a skill your module invokes goes in `required_skills`).** Today `bmod.toml` requires
only `bmad` and lists `bmad-review` as recommended.
- `ogcspec-review` invokes `bmad-review`, so `bmad-review` moves to required.
- `EL` needs `bmad-advanced-elicitation` (core).
- `DC` needs the `decision-record` template and step 8 needs `bmad-walkthrough`. Per `skills-and-agents.md` both come with the BMad
  Method module (`bmod-method`), which would then become a dependency of this module, together with everything it brings.
  Alternatives: ship our own decision-record template with the module, and make the walkthrough a recommended step. **open** Then `validate_manifests.py` from the pin and `init_skill.py --check --any-name`.
Skill names starting `ogcspec-` pass only with `--any-name` (existing finding in `README.md`).

## Workflow

Existing tools are named; **new** marks something that does not exist yet.

| # | step | who/what | tool |
|---|---|---|---|
| 1 | Describe the behaviour and pick the class boundaries | human + Architect | `ogcspec-modspec` |
| 2 | Draft records with proposed identifiers | Architect | `ogcspec-modspec` |
| 3 | Stage-1 gate | script | `gate.py --config … --baseline …` |
| 4 | Independent review | fresh readers | `ogcspec-review` (**new**) |
| — | **H1, H2, H4** as they apply | human | see below |
| 5 | Emit AsciiDoc fragments | script | `emit.py --records … --out …` |
| 6 | Compile **a copy** of the repository | script | `metanorma.py --image … --adoc … --formats xml [--root …]` |
| 7 | Stage-2 gate | script | `gate.py … --xml … --compile-result …` |
| 8 | Human walk-through of the diff | human | `bmad-walkthrough` (description only; **not read**) |
| — | **H5** commit | human | git |
| 9 | Authoritative check | CI | the standard's repository CI (**never run**; this repository's workflow has not executed) |
| — | **H6** anything sent to OGC | human | outside this module |

Steps 5–7 compile in a copy because compiling in place rewrote tracked files (the compiled XML and `relaton/cache`) in the ModSpec clone; this is recorded in `skills/ogcspec-metanorma/SKILL.md`, and I did not reproduce it.

### Human gates: hard stops

Each is a point where the agent stops, states what it needs, and takes no further action on that item. Agents do not pass a
gate on a user's general "go ahead"; approval is per item and is recorded in the repository (a decision record, a
human-edited file or a human's commit) so it can be seen later. **inferred**

| gate | the agent must not | what the human does |
|---|---|---|
| **H1 identifiers** | mint an identifier or `opengis.net` URI, call one assigned or registered, or file anything with the Naming Authority | accepts, renames or rejects each proposed identifier |
| **H2 normative wording** | finalize a `statement` or test `steps`, or choose a verbal form for a provision | reads and edits the text; accepts per record |
| **H3 gate configuration** | edit the baseline, add a `[[normative_references]]` entry, change `core_dependency`, or change a pin | decides and edits the file |
| **H4 contested readings** | pick between two readings (Req 22 direct vs transitive, Req 27/28 against documents listing another class's requirement) | decides; the decision is recorded (`DC`) |
| ~~H5 commit~~ | *Not a module hard stop (owner decision 3): left to the standard repository's rules.* | reads the diff before it is committed, as the repository requires |
| **H6 outbound** | send, post or file anything to OGC, the ModSpec maintainers, an upstream repository or the SWG, including the five questions in `PLAN.md` | sends it themselves |

**What actually enforces these (inferred; not tested).** The persona text is advisory: it can be overridden by a user message
and nothing checks that it held. Mechanical enforcement is possible only where the artifact is a file:
H3 and H5 by repository permissions and review rules (needs a remote and CI, **open**); H1 only if the gate learns an
"approved identifiers" file and fails on records outside it (**new**, **open**, would belong in plan step 3). H2, H4 and H6
rest on the human. This should be said in `help.md` and not left implied.

**Tests for the gates (open).** `bmad-eval` could run cases in which the user asks the Architect to mint an id, edit the baseline
or send a question to OGC and the correct result is a refusal and a hand-off. These have not been written or run; running
evals spends model tokens and is the owner's call.

## Dependencies and open items

- **Record format (plan step 2) is not done.** Personas would draft records in today's format (`ogcspec-modspec` SKILL.md:
  `requirements_class`, `requirement`, `abstract_test`, `conformance_class`, …). If step 2 changes the format, `DR`, `TR` and
  `ogcspec-review` change with it. **open**
- A `status: proposed|accepted` field, or equivalent, does not exist in records, so the gate cannot tell an unapproved record from an approved one. **open**
- Whether the Architect should call the Req 22 switch at all or only report the three states. Current gate reports; H4 decides.
- Whether non-record clauses (scope, terms, references, annexes) are written by agents. Decides the Editor persona.
- The earlier feasibility report **states**, citing OGC 05-020r29 §§4.13, 8.4 and 8.8 together, that "non-OGC private
  repositories or projects may not be used for development of SWG deliverables". Its further remark that an agent pipeline
  should then run inside the OGC-controlled environment is that report's own inference. I did not check either; if both hold,
  they constrain where this workflow may run once an SWG exists.
- Left to the owner as before: `npx skills add` install, licence, the five OGC questions, CI.

## Decisions made by the owner (2026-11-06, in session)

These override the recommendations above where they differ.

1. **Persona set: Architect + Editor + `ogcspec-review`.** (The recommendation was Architect + review first.) Because no skill yet
   holds know-how for non-record clauses, the Editor's menu is limited to build items (`EM` emit, `CP` compile a copy, `G2`
   stage-2 gate, `X` triage Metanorma messages) and `SB`, which prepares a submission pack as a draft file and sends nothing.
   The Architect keeps a `BUILD` item as a shortcut. Drafting non-record clauses stays out of scope until a skill exists for it.
2. **Names: role names only.** "ModSpec Architect" and "Metanorma Editor". Icons are mine to propose in the scaffold; the owner
   did not name any. Skill names are `ogcspec-agent-architect` and `ogcspec-agent-editor`.
3. **Commit (H5) is not a module-level hard stop.** The module says nothing about committing; the standard repository's rules
   and the user's own Claude Code settings decide. H1–H4 and H6 remain hard stops. The earlier worry that OGC puts accountability
   on named people is the feasibility report's reading (**stated**, not checked) and is not enforced by this module.
4. **Add a `decisions_dir` setup question** (default `docs/decisions`) for H4 decision records.
5. **Require the BMad Method module.** Read at the pin: `bmad-walkthrough` is a member skill of `bmod-method`;
   the decision-record template is `skills/bmod-method/doc-templates/template-decision-record.md`; `bmad-facilitate`
   (which offers templates) is in `bmod-core-tools`. The module record's `required_skills` takes skill names, so requiring
   `bmad-walkthrough` is the likely way to require the Method module. Whether setup then installs the whole module, and the
   right version string (the Method record is `6.13.0-next`), are **open** and need a `validate_manifests.py` run on the scaffold. Consequence to state in
   `help.md`: users install every Method skill, and v7 alpha changes reach this module through it.
6. **Review without subagents runs and is labelled.** The report must begin "NOT INDEPENDENT: reviewed in the drafting
   conversation" when subagents are unavailable.

Still open: the record format (plan step 2), a proposed/accepted status on records, which `bmad-review` lenses run, and the
owner-only items (`npx skills add`, licence, the five OGC questions, CI).
