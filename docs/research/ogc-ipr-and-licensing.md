# OGC rules on contributed material, read against the MIT choice

Read 2026-11-07 by a research subagent (web only), at the owner's request (decision 6 of 8). **Not legal advice.** It makes no finding of
conflict or of no conflict. Treat everything below as a lead to check, not a conclusion.

**How reliable the quotes are.** The fetch tool summarises pages with a small model. The agent extracted the two primary documents (the IPR
Policy PDF and the TC Policies and Procedures HTML) to scratch files and quoted from those; the other pages (items 8-11) are as the tool relayed
them and are less certain. **Not opened:** the OGC Software IP Policy (which IPR section 1.3 cites) and the OGC Membership Agreement. I (the
main agent) did not re-read any source for this note; check the quotes against the links before relying on them.

## What the sources say

1. **Scope.** The IPR Policy (revised 15 Dec 2021) "applies only to activities undertaken by Standards Working Groups and Working Groups." Software
   contributed to a SWG for inclusion in a Candidate Standard or Standard is covered; other software (tools, reference implementations) is governed
   by "the OGC Software IP Policy and as otherwise specified in the charter of such Standards Working Group" (section 1.3).
   <https://docs.ogc.org/pol/Intellectual_Property_Rights_Policy_revised_15_December_2021.pdf>
2. **Who is bound.** "All Members, all Member Representatives, and all third parties participating in an OGC Working Group are subject to this
   Policy" (section 1.2).
3. **Text contributions.** The Contributor "grants to OGC a perpetual, irrevocable, non-exclusive, royalty-free, worldwide copyright license, with the
   right to directly and indirectly sublicense ... and to prepare derivative works ... solely for the purpose of developing and promoting an OGC
   Standard" (section 4.2). Copyright in Standards "shall belong to OGC, subject to the underlying ownership rights of Contributors" (section 4.1).
4. **Software contributions.** An Appendix D form is required (4.3(a)). The Contributor may "assign the copyright ... to OGC, or ... retain copyright
   ownership" (4.3(b)); on assignment OGC grants back a licence to fully exploit it (4.3(c)); software in a Standard "should be presumed informative"
   (4.3(d)); absent Board approval it "shall be licensed by OGC under the OGC License" (4.3(e)), which is BSD-3-style (Appendix E).
5. **Patents.** Each Contributor must commit to license patent claims that become Necessary Claims (3.2); contributions are "non-confidential and
   non-proprietary" (5).
6. **TC Policies and Procedures 05-020r29, sections 3.6.4 and 4.13.7.** Public SWG repositories must show: "The contributor understands that any
   contributions, if accepted by the OGC Membership, shall be incorporated into OGC Standards or other documents and that all copyright and
   intellectual property shall be vested to the OGC." Also: "Non-OGC private repositories or projects may not be used for development of SWG
   deliverables." <https://docs.ogc.org/pol/05-020r29/05-020r29.html>
7. **Submissions.** Candidate Standard submitters "grant OGC a non-exclusive, royalty-free, paid-up, worldwide license to copy and distribute their
   submission ... and, if adopted by OGC, the right to modify, enhance, and make derivative works". A Statement of Technology form may be required.
8. **Published OGC documents.** "No right to create modifications or derivatives of OGC documents is granted pursuant to this license." Copies must
   keep a link to the original and the copyright notice. <https://www.ogc.org/about-ogc/policies/document-notice/> (via summariser)
9. **Software licences OGC lists:** "OGC software license 1.0" (deprecated, 2001) and "Apache Software License 2.0" (from 2004).
   <https://www.ogc.org/about/policies/software-licenses/> (via summariser)
10. **Practice on GitHub.** Three opengeospatial repositories checked (bblocks-postprocess, CoverageJSON, geoparquet) show Apache-2.0. The
    ogcapi-features CONTRIBUTING repeats the "vested to the OGC" statement and, per the fetch, mentions no CLA or DCO. (via summariser)
11. **Third-party material.** ogc-modspec README: "These documents are published by the OGC. The copyright of such documents remain unchanged. All
    other code and information, copyright Ribose." metanorma-ogc is BSD-2-Clause, per the fetch. (via summariser)

## Inference (the agent's and mine, not OGC's)

- Using the tool privately, or publishing it separately under MIT, does not obviously touch these rules; they attach to Contributions made to a SWG
  or Working Group.
- Contributing the template or generated text into an SWG repository would likely meet the section 3.6.4 "vested to the OGC" statement. That reads as a
  copyright transfer, which sits awkwardly with section 4.2 of the IPR Policy, where the contributor keeps ownership and grants a licence. An
  MIT-licensed contribution would presumably need the tool kept outside the SWG repository, or an explicit OGC decision.
- If an SWG treats the tool as "Software", the Appendix D election and the OGC License (4.3(e)) could apply; that differs from MIT.
- MIT is irrevocable once published: copies already distributed stay MIT even if OGC later holds copyright in a contributed version.
- This repository quotes OGC text only in short notes; the document-notice no-derivatives clause favours keeping it that way, with the notice and link.
- Generated requirement text, if submitted, is probably a Contribution, with ownership depending on who authored it. Treatment of AI-assisted
  authorship is not addressed in anything found.

## Not found

An OGC CLA or DCO; any organisation-wide GitHub licence rule; any OGC statement on AI-generated contributions; the Software IP Policy text; the
Membership Agreement text.

## Questions for OGC staff or a lawyer (the owner's to put)

1. Is a tool used to author an SWG standard "Software" under IPR section 1.3, and which policy governs it?
2. Does the section 3.6.4 statement mean copyright assignment, or only the section 4.2 licence, for text contributions?
3. May a contributor keep an upstream MIT repository and contribute only specific files? Is an Appendix D election with grant-back sufficient?
4. Does an SWG charter override the default software licence (OGC License, Apache-2.0 or MIT)?
5. Do OGC documents allow requirement text to be generated or stored in the tool's format when OGC grants no derivative rights in published documents?
6. How is AI-assisted drafting treated for the "necessary rights and authority" warranty in Appendix D?
7. Is a Statement of Technology form needed if the template is submitted?

## What changes in this repository

Nothing. The licence stays MIT (owner's decision). The practical consequence is that the MIT choice looks safe for an independent tool and
unsettled for anything contributed into an SWG; `CLAUDE.md` already says nothing here is endorsed by or registered with OGC.
