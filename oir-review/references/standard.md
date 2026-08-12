# The report standard

Contents: [Section structure](#section-structure) · [BLUF](#bluf-the-first-150-words) ·
[What goes where](#what-goes-where) · [What stays out](#what-stays-out) ·
[Report states](#report-states-interim-final-superseded) · [Adapting to a house template](#adapting-to-a-house-template)

## Section structure

Eight sections. Mature teams converge on roughly this set regardless of
industry, and the ordering is not arbitrary — it runs answer, then scope, then
evidence, then interpretation, then consequence, so a reader can stop at any
point and be correctly informed for their level of interest.

| # | Section | Answers |
|---|---|---|
| 1 | Bottom line | What happened, how bad, what do you need from me? |
| 2 | Scope, authority and status | What was investigated, under whose authority, is this interim or final? |
| 3 | Timeline | In what order, at what UTC times, on what evidence? |
| 4 | Findings — observed | What do the artifacts show? Facts only. |
| 5 | Assessments — judged | What do we infer, with what likelihood and what confidence? |
| 6 | Impact and affected scope | Who and what was affected, bounded by what was searched? |
| 7 | Limitations and collection gaps | What could we not see, and what would change these conclusions? |
| 8 | Evidence register | Every artifact, with source, hash, query, retrieval time. |

The split between §4 and §5 is the load-bearing structural decision in the
whole standard. It is the mechanism that keeps a junior analyst's hunch about
attribution from becoming an exhibit — not because anyone is forbidden from
having a hunch, but because the hunch lives in a section labelled as such,
with a likelihood term attached.

**Regional and regulatory annexes** go after §8, each with an explicit
applicability line: "Complete only if EU data subjects are in scope",
"Complete only if the entity is NYDFS-covered". A distributed team needs the
same eight sections everywhere and different annexes by region — trying to
make one template carry every jurisdiction's fields produces a form nobody
fills in.

A **remediation plan is a separate document.** See `legal-exposure.md` for why
this is not a formatting preference.

## BLUF: the first 150 words

The bottom line goes in the first or second paragraph — DA PAM 600-67 §3-1a,
carried forward into AR 25-50 ¶1-38.b as one of two "essential requirements"
of Army writing. The reason it survived sixty years is that executives, audit
and counsel read the top and stop, and the version they carry into a decision
is whatever was in the first paragraph.

An OIR bottom line carries five things, in one short block:

1. **Severity** from the house taxonomy, with the taxonomy named.
2. **One sentence of what happened**, in the plainest available English.
3. **The determination status** — determined / assessed / under investigation.
   This is a term of art, not a synonym set; see `legal-exposure.md`.
4. **The decision being asked for**, or "no decision required".
5. **Report status** — interim or final, and the version.

Worked example:

> **Severity: High** (house scale, §Severity). Between 2026-07-14T02:11:00Z and
> 2026-07-17T19:40:00Z, an external actor authenticated to three
> internet-facing VPN accounts using valid credentials and accessed a file
> share containing internal engineering documentation. **No evidence of
> customer data access was observed** in the sources and window described in
> §7. **Status: under investigation** — a Reg S-P sensitive-customer-information
> determination has not yet been made and is expected by
> 2026-07-31T17:00:00Z. **Decision required:** whether to engage outside
> counsel before the next interim. Interim report v0.3.

Note what that paragraph does not do: it does not say "breach", it does not
name an actor, it does not say "we responded immediately", and its negative
finding is bounded by a pointer to the section that states what was searched.

## What goes where

**§3 Timeline.** One row per event. Columns: UTC timestamp (RFC 3339),
event, source system, evidence ID. Nothing in the timeline that is not
anchored to an artifact — inferred events belong in §5 with an explicit note
that they are reconstructed. Where clock skew was measured, state it
numerically with how it was measured.

**§4 Findings.** Each finding: a declarative sentence about what an artifact
shows, plus the evidence ID, plus the window the source covers. If you find
yourself writing "which suggests", you have crossed into §5.

**§5 Assessments.** Each assessment: the judgment with a likelihood term and
inline numeric range; a separate sentence giving confidence and what drives
it; the alternatives considered and what discriminates between them; and the
indicator that would change the assessment. Four moves, and all four are
required — see `estimative-language.md`.

**§6 Impact.** Systems, accounts, records, services. Every count bounded by
what was searched. "Affected" and "potentially affected" are different
columns, not different adjectives in the same sentence.

**§7 Limitations.** Log retention per source, coverage gaps, hosts not
imaged, sources whose local offset could not be recovered, tooling
limitations, SOP deviations (SWGDE 18-Q-002 §5.4 requires deviations be
disclosed), and the indicators that would change the report's conclusions.
This section is the one most often skipped and the one that most determines
whether a negative finding survives contact with a regulator.

**§8 Evidence register.** See `evidence.md` for the field list.

## What stays out

- **Remediation recommendations.** Separate document.
- **Control adequacy judgments.** "Logging was insufficient" is a
  legal/regulatory conclusion. Describe the control's configuration and its
  observed behaviour; let the regulator draw the conclusion.
- **Blame.** Root cause is a condition, not a person. "The patch management
  control did not execute for Asset Group A because of an approval-workflow
  exception" — not "the platform team missed it."
- **Policy-conformance assessment.** "Our policy requires X and we did Y" is a
  self-generated compliance-gap admission. Facts here; conformance in a
  separate, counsel-directed document.
- **Unqualified attribution.** See `estimative-language.md`.
- **Raw tool output with no relevance filtering.** SANS calls this "link
  dumping". If a 400-line export matters, cite it in §8 and quote the six
  lines that carry the finding.
- **Editorial adverbs.** Fortunately, unfortunately, alarmingly,
  surprisingly. The report records what happened; it does not decide whether
  that was good.

## Report states: interim, final, superseded

Interim conclusions that later change are the most-cited text in litigation,
because they get read against the final conclusions. Three rules make that
survivable:

1. **Version and date every draft**, in the document, not just the filename.
2. **Mark supersession explicitly.** When an interim judgment changes, say so
   and say why: "v0.2 assessed initial access as likely (55-80%) via the
   phishing message [E4]. v0.3 revises this to unlikely (20-45%) following
   recovery of VPN authentication logs [E17], which show first access
   19 hours before the message was delivered." ICD 203 tradecraft standard 7
   asks for exactly this, and it is what converts a wrong early call from an
   embarrassment into evidence of a functioning process.
3. **Never silently edit an issued version.** Issue a new one.

## Adapting to a house template

If the team has a template already, review against theirs and use this one to
identify gaps rather than to replace it. The advice Meg Anderson gave is
right: start from the best template in use today, note what is missing and
what is extra, ship version 1, and review annually. A standard that arrives
as a replacement gets resisted; a standard that arrives as three additions to
the form people already fill in gets adopted.

When mapping a house template to this standard, the questions worth asking
are only these:

- Is the conclusion and severity at the top?
- Is there a structural separation between observed and assessed?
- Is there a limitations section?
- Is there an evidence register with enough to reproduce a finding?
- Are remediation recommendations somewhere else?

Everything else is formatting.
