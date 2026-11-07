# Identifiers and class membership: what ModSpec requires and what real documents do

Read from ModSpec Part 1 (08-131r7) and the ModSpec Policy (25-001, a draft) on 2026-11-06:

- A requirement belongs to exactly one requirements class, and the class's `requirement::` list says which
  (Req 28, ATS 15). Nothing requires an identifier to carry its class's name as a prefix.
- Every component needs a unique identifier or label (Req 2). Requirements are denoted by partial URIs relative to
  the document's namespace (clause 5); the draft Policy asks for unique URIs that follow the OGC Naming Authority's
  policies. A person mints and approves them.
- Requirements classes and conformance classes correspond one-to-one (Req 8); a conformance class tests all the
  requirements of its class and only that class's (Reqs 11, 15); every requirement has a test (Req 1, clause 8.5).

What the real documents do (Processes, Records, Connected Systems, ModSpec itself):

- Class ids are often absolute (`https://www.opengis.net/spec/<name>/<ver>/req/core`) while members are relative
  (`/req/core/x`). Set `namespace` in the gate config so the two compare equal; the gate never guesses it, and does
  not treat `http`/`https` or `_`/`-` as equal.
- Members usually, but not always, share their class's prefix; ModSpec's own class is `req-class-core` with members
  under `/req/core/`. So the default rules use listing, and the prefix convention is the opt-in `style = ["prefix"]`.
- `inherit` may name a class by its title (Records), by an absolute URI (external standards), or by a bare citation.
- A conformance class may point at its requirements class with an xref (`subject::`) rather than `target::`.

For records authored with this module the `/req/<class>/<name>` shape is a good habit, and `style = ["prefix"]`
checks it, but no OGC document requires it. Do not rewrite an imported OGC document's identifiers to match it.
