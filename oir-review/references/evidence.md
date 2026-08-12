# Evidence, timestamps and the register

Contents: [Timestamps](#timestamps) · [Clock skew](#clock-skew) · [The evidence register](#the-evidence-register) ·
[Chain of custody](#chain-of-custody) · [Citing evidence in the body](#citing-evidence-in-the-body) ·
[Retention and negative findings](#retention-and-negative-findings)

## Timestamps

**Specify RFC 3339, not "ISO 8601".** RFC 3339 is a strict profile of ISO
8601 — ISO 8601 also permits the basic format (`20260729T041300Z`), week
dates, ordinal dates, reduced precision and comma decimal separators, all of
which reintroduce the ambiguity you were trying to remove. If a house standard
says "ISO 8601", it has not actually specified one form.

House rule:

- Every timestamp in the report body: **RFC 3339, UTC, `Z` suffix**, with
  sub-second precision where the source provides it —
  `2026-07-29T04:13:00.523Z`.
- **Preserve the original local offset** in the evidence register. The offset
  carries analytic signal: it tells you about operator working hours and the
  actor's likely time zone. Normalising it away destroys information.
- Where the source's local offset **could not be recovered**, RFC 3339 has a
  specific convention for exactly this and almost nobody uses it: an offset of
  `-00:00` means "the UTC time is known but the local offset is not", which is
  semantically different from `Z` or `+00:00`. Use it, and note it in §7.
- Leap seconds are legal (`1990-12-31T23:59:60Z`) and do appear in
  NTP-disciplined logs. Naive parsers reject them.

Anything that looks like `07/29/2026`, `4:13 PM EDT`, `Jul 29, 2026`, or a
bare `2026-07-29 04:13` with no zone is a hard finding. On a distributed team
`07/29/2026` is not merely ambiguous, it is *differently* unambiguous
depending on who reads it.

## Clock skew

NIST SP 800-92 states the failure precisely: *"timestamps might indicate that
event A happened 45 seconds before event B, when event A actually happened two
minutes after event B."* Clock error does not blur a timeline — it inverts
causality, which is fatal to a report whose central claim is an attack
sequence.

So:

- State measured skew numerically, with how it was measured: "`WKS-4471` local
  clock was +00:04:17 ahead of the NTP source, measured at acquisition against
  `time.internal.example` [E14]. Timeline entries from this host have been
  adjusted."
- If skew was not measured on a host whose timestamps carry a causal claim,
  say so in §7. An unmeasured clock is a limitation, not a footnote.
- Where a causal ordering rests on a sub-minute gap between two systems whose
  relative skew is unknown, the honest form is an assessment with a likelihood
  term, not a timeline row.

## The evidence register

Every item that any finding rests on. SWGDE 18-Q-002 §5.3 asks for enough to
"uniquely identify each item submitted or collected" — serial numbers, hash
values, or equivalent. This is the reproducibility contract: a regulator, an
auditor or opposing counsel can ask you to run it again.

| Field | Why |
|---|---|
| Evidence ID (`E12`) | referenced from the body |
| Source system — FQDN, role, owner | uniquely identify the item |
| Log type / product / **version and build** | tool behaviour changes between versions; "Cellebrite Physical Analyzer v7.13 (build 6600)" not "Cellebrite" |
| **Exact query or filter**, verbatim | reproducibility; NIST SP 800-86 wants every step including each tool used |
| Retrieval timestamp, RFC 3339 UTC | when this snapshot was taken |
| Native timezone of the source, and whether normalisation was applied | see above |
| Record count returned | lets someone check they got the same thing |
| **Hash of the exported artifact**, algorithm named | integrity; NIST SP 800-86 message digest |
| Retention window, and whether data has since aged out | bounds every negative finding |
| Analyst identity and custody handoffs | chain of custody |
| **Any SOP deviation** | SWGDE §5.4: deviations *must* be disclosed |

The register is also where you record what you *could not* collect and why.
A host reimaged before acquisition, a cloud log with 7-day retention that
aged out during the investigation, an EDR sensor that was not deployed — these
belong in the register and in §7, not in a verbal aside.

## Chain of custody

Per NIST SP 800-86: a log of every person who had custody, what they did, and
when; a single designated evidence custodian; every collection step recorded
including the tool used; integrity verified by comparing message digests of
original and copy. ISO/IEC 27037 frames the same requirement as four
properties the record must satisfy — auditability, repeatability,
reproducibility, justifiability.

For most operational investigations a full forensic chain of custody is
disproportionate. The proportionate version is: the register above, plus a
named custodian, plus a hash at export. What is *not* optional is
**disclosing which standard of handling was applied**, because a report that
implies forensic rigour it did not apply is worse than one that says "logs
were exported by the on-call analyst without formal custody; this is
sufficient for operational purposes and would not meet an evidentiary
standard."

## Citing evidence in the body

No single authority prescribes a citation format; the following is composed
from SWGDE §5.3, NIST SP 800-86 and DFIR practice.

Inline, use a short reference to the register: `[E12]`. Reserve the full
citation for the register itself. What matters is that:

- Every finding in §4 carries at least one evidence reference.
- Every assessment in §5 either carries evidence references or explicitly says
  it is inferential.
- The reference supports **the specific claim in that sentence**, not a
  weaker adjacent one. This is where most review findings come from.
- Where a claim rests on the *absence* of something, the reference points to
  the source searched, not to nothing.

Do not link-dump. SANS names this failure directly: pasting raw tool output
without relevance filtering. If a 400-line export matters, put it in the
register and quote the six lines that carry the finding.

## Retention and negative findings

The most important interaction in this whole file. A negative finding is only
as strong as the window it was searched over, and readers — especially
executives making a materiality call — routinely read "no evidence of X" as
"X did not happen."

Every negative finding states:

1. Sources searched, by evidence ID.
2. The exact window searched.
3. **The retention boundary of each source** — where does the data stop
   existing?
4. Coverage gaps within the window.
5. What the absence does and does not support.

> No evidence of database export was observed in `db-audit-01` and
> `db-audit-02` query logs [E31, E32] covering 2026-06-14T00:00:00Z to
> 2026-07-18T00:00:00Z. Retention on both sources is 35 days, so activity
> before 2026-06-13 cannot be assessed from this source. Audit logging on
> `db-03` was not enabled until 2026-07-02T14:00:00Z [E33]. These findings do
> not exclude export via a path not covered by database audit logging; see §7.

That version survives a deposition and a regulator. "No data was exfiltrated"
does not, and the difference between them is about ninety seconds of writing.
