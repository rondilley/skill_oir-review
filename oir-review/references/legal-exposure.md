# Legal and regulatory exposure

Contents: [Assume it will be produced](#assume-it-will-be-produced) · [The four fatal content patterns](#the-four-fatal-content-patterns) ·
[Substitution table](#substitution-table) · [Determined, assessed, under investigation](#determined-assessed-under-investigation) ·
[US financial services clocks](#us-financial-services-clocks) · [Caveats](#caveats)

> This is drafting guidance assembled from published case law and law-firm
> practitioner guidance. It is not legal advice, and the substitutions in the
> table below should be reviewed by the organisation's counsel before being
> adopted as a house standard. Verify the regulatory status items — several
> are in motion.

## Assume it will be produced

Four decisions, one direction of travel:

**In re Capital One** (E.D. Va., May 2020, aff'd June 2020) — Mandiant report
ordered produced. Work product failed the Fourth Circuit "but for" test:
Capital One could not show the report "would not have been prepared in
substantially similar form but for the prospect of litigation." The dispositive
facts were structural — a pre-existing MSA whose terms were virtually
identical to the post-incident letter agreement, a stated business-critical
need for the information, distribution to regulators, auditors and roughly 50
employees, and payment from the pre-existing retainer with the expense only
later reclassified as legal.

**Wengui v. Clark Hill** (D.D.C., Jan. 2021) — the "two-track" case. The firm
claimed a business track and a legal track; the second track was illusory,
there was no sworn statement that the business vendor conducted a separate
investigation, and the firm conceded its understanding of the incident came
solely from the legal-track vendor. Attorney-client privilege also failed,
partly because the report contained "pages of specific recommendations on how
[the Firm] should tighten its cybersecurity" — operational remediation, not
legal advice.

**In re Rutter's** (M.D. Pa., July 2021) — Kroll report produced under the
Third Circuit "primary motivating purpose" standard. The killer fact was
testimonial: the Rule 30(b)(6) corporate designee testified Kroll "would have
done this work and prepared its incident response investigation regardless of
whether or not lawsuits were filed." The court also noted "the attorney-client
privilege does not protect the communication of facts."

**Leonard v. McMenamins** (W.D. Wash., Dec. 2023) — most recent significant
erosion. Report contained "only factual information" with no legal advice;
counsel's engagement of the firm was immaterial. Emails between counsel and
the forensic firm *discussing the facts of the attack* were also held not
privileged.

Protection has been upheld — *In re Target* (D. Minn. 2015), with a genuine
two-track structure where the PCI-mandated investigation was produced and a
separate counsel-directed task force was not; *In re Experian* (C.D. Cal.
2017), where decisively the full report was **not** provided to the internal
incident response team. Both counterexamples turn on real separation, which
an operational SOC report by definition does not have.

The practical conclusion for an analyst: **the operational investigation report
is a business document and should be written as one that will be read by a
hostile reader.** A privilege legend does not change this — Capital One, Clark
Hill and Rutter's all carried one.

## The four fatal content patterns

1. **Remediation recommendations inside the investigative report.** *Clark
   Hill* treated them as proof the document served operational rather than
   legal purposes. And once produced, the recommendations themselves become
   the roadmap: they knew what to fix and here is the date they wrote it down.
   Separate document.
2. **Characterisations of the organisation's own security posture.** "Logging
   was insufficient", "the control was not effective", "this was preventable"
   — adequacy is a legal and regulatory conclusion. Describe **control state**,
   not **control adequacy**.
3. **Attribution guesses.** Creates a discoverable statement the organisation
   may later contradict in an 8-K or regulator filing, and sanctions exposure
   if a payment follows.
4. **Speculation and hyperbole in interim findings.** Early hypotheses that
   turn out wrong are the most damaging text in the file, because they get read
   against the final conclusions. Akin Gump: "A written report that rests on
   conjecture and unsupported initial findings will not be helpful in future
   litigation."

The governing formulation, from Squire Patton Boggs: forensic reports should
contain "only the facts, as supported by forensic findings" and should exclude
"recommendations for further investigation and remediation; information that
is speculative; or opinions."

Note the tension with analytic tradecraft: ICD 203 wants assessments and
alternatives. The resolution is not to omit judgment but to **mark it
structurally** — assessments live in their own section, each carrying a
likelihood term, a range, a confidence statement and its alternatives. A
marked, calibrated assessment is defensible. An unmarked hunch in the middle of
a findings paragraph is not.

## Substitution table

| Avoid | Why | Use instead |
|---|---|---|
| breach | Statutorily defined, and defined *differently* by each regulator. Train the org to say "incident" until counsel says "breach". | "incident"; "unauthorized access to X"; "exposure of Y records" |
| failed to, failure of | Reads as an admission of fault | "did not execute", "did not generate an alert", "was not configured to" |
| negligent, reckless, careless | Legal standards of care | omit; describe the control state |
| should have, could have prevented, if only | Counterfactual = admission | "the control as configured did not…"; remediation goes elsewhere |
| we knew, was known, previously identified | Establishes notice — the plaintiff's key element | the artifact and its date: "Ticket #1234, opened 2026-03-02, referenced CVE-XXXX on Asset Group A" |
| root cause was [person/team] | Blame, and speculative as to intent | condition-action-evidence: "The patch management control did not execute for Asset Group A due to an approval-workflow exception, leaving CVE-XXXX unremediated" |
| inadequate / insufficient / weak controls | Adequacy is a legal conclusion | the control's actual configuration and observed behaviour |
| the attacker was [APT-NN] | Speculative attribution; sanctions exposure | "Observed TTPs overlap with public reporting on [X]. We assess roughly even chance (45–55%). Confidence: Low." |
| no data was exfiltrated / no risk / impossible | Unbounded absolute; one contrary log kills it | "No evidence of exfiltration was observed in [sources] covering [window]. Retention for [source] begins [date]." |
| compromised (loosely) | Claims a confirmed CIA loss | match the verb to the evidence: "authenticated to", "executed on", "accessed" |
| immediately, as soon as we learned | Invites contradiction by the timeline | absolute RFC 3339 UTC timestamps |
| obviously, clearly, of course | Hyperbole; flagged in privilege guidance | delete |
| we recommend, must fix, urgent remediation | Turns the report into a business document (*Clark Hill*) | separate remediation plan |
| our policy requires X and we did Y | Self-generated compliance-gap admission | facts here; conformance assessment elsewhere |

The right-hand column is drafting guidance, not published authority. Have
counsel review it before it becomes house standard.

## Determined, assessed, under investigation

These are three different words and in US financial services they have
different consequences, because several regulatory clocks start at
**determination** rather than at discovery.

- **Determined** — a formal organisational decision has been made. Timestamp
  it and name the role that made it: "Determined at 2026-07-29T14:00:00Z by
  the Incident Commander."
- **Assessed** — an analytic judgment with a likelihood and confidence. Not a
  determination.
- **Under investigation** — no judgment yet. Say when one is expected.

A report that uses "determined" loosely either starts a clock nobody noticed
or fails to start one that should have run. A report that never timestamps its
determinations leaves the organisation unable to show when the clock started.
The linter flags this.

## US financial services clocks

Include enough in the report for someone to make these calls; do not make them
in the report.

| Trigger | Clock | Keyed to |
|---|---|---|
| **SEC Item 1.05, Form 8-K** | 4 business days | the *materiality determination*, which must itself be made "without unreasonable delay" after discovery |
| **NYDFS 23 NYCRR §500.17(a)** | 72 hours | determining a cybersecurity incident occurred (including at an affiliate or third-party service provider) |
| **NYDFS extortion payment** | 24 hours, plus a written description within 30 days | the payment |
| **Banking agencies (OCC/FRB/FDIC), 12 CFR 53 et al.** | 36 hours | determining a "notification incident" occurred |
| **SEC Reg S-P §248.30(a)(4)** | as soon as practical, ≤30 days | becoming aware sensitive customer information was, or is reasonably likely to have been, accessed without authorisation |
| **Reg S-P service provider** | 72 hours | the provider becoming aware |
| **GLBA Safeguards / FTC** (non-banking FIs, ≥500 consumers) | ≤30 days | discovery |
| **CIRCIA** (statutory; final rule still pending) | 72 hours / 24 hours for ransom payment | reasonable belief the incident occurred / the payment |
| **State breach notification** | fastest are ~10–30 days | varies |

Two report-design consequences:

**The report has to support a fast determination.** With a 36-hour banking
clock and 72-hour NYDFS and CIRCIA clocks, the facts that drive a
determination must be findable in the first page, not buried in a findings
section. This is the operational argument for BLUF, separate from the
readability one.

**Reg S-P is the most-missed field.** An OIR at a US financial-services firm
should affirmatively answer: was sensitive customer information accessed or
reasonably likely accessed, and is the "not reasonably likely to result in
substantial harm or inconvenience" determination documented? That
determination is itself a discoverable artifact. Most templates have no field
for it.

Distinguish the layered definitions rather than collapsing them: NYDFS
"cybersecurity event" includes *unsuccessful* attempts; the banking agencies'
"computer-security incident" requires *actual harm*; SEC uses "cybersecurity
incident" per Reg S-K 106(a); GLBA uses "notification event". An analyst
writing "breach" collapses four different legal triggers into one word.

## Caveats

- **CIRCIA's final rule was not published as of this writing**; the 72-hour and
  24-hour clocks are statutory and stable, but covered-entity scope and
  required report contents are not final. Verify current status.
- **SEC Item 1.05 has a pending rescission petition** (File No. 4-856) that has
  not been acted on. Assume 1.05 is live; re-verify periodically.
- **NIST SP 800-61r3 (April 2025)** is a CSF 2.0 Community Profile and drops
  r2's field lists and categorisation tables. Cite r3 (RC.RP-06, RS.AN-06/-07,
  RS.CO-02/-03) for governance framing and r2 for the field-level checklists.
- The privilege line has not visibly shifted in 2024–2026, but that is from a
  survey rather than a citator sweep. The report should not assert the law is
  settled; it should assume production.
