# Sourcing review, not readability review

Contents: [Why this is the main event](#why-this-is-the-main-event) · [The claim ledger](#the-claim-ledger) ·
[Attribution drift](#attribution-drift) · [The six overclaim patterns](#the-six-overclaim-patterns) ·
[Negative findings](#negative-findings) · [What not to do](#what-not-to-do)

## Why this is the main event

Teams draft with AI now. That solves the grammar problem the training
programme was aimed at and creates a worse one: confident prose asserting more
than the evidence supports.

Hagar, Agustianto & Diakopoulos (2025) tested three document-grounded LLM
systems against a source corpus, producing 40 responses. Twelve were wrong —
30% — with the two general assistants at 40% each and a purpose-built RAG tool
at 13%. About two-thirds of the erroneous responses introduced significant
inaccuracy. (It is a small study and an unrefereed preprint; treat the
mechanism as the finding and the percentages as indicative.) The important
part is *what kind* of error:

> The two dominant error types were not fabricated facts. They were
> **editorialising about sources** — confident characterisations of a
> document's purpose or content with no textual basis — and **attribution
> drift**, "transforming attributed opinions into universal statements,
> stripping away crucial source attribution."

Neither is visible to a readability metric. AI-drafted prose scores *better*
on Flesch-Kincaid precisely while it is drifting attribution. The check has to
be claim-to-source, not word-to-syllable.

This is also why the review must not be stylometric. "Delve", em-dash density,
uniform sentence length — these markers false-positive hard on analysts
writing in a second language or using translation tools, who produce the same
surface features (elevated formality, uniform length, heavy connectives). A
stylometric rule punishes the wrong people. Trace the claims instead.

## The claim ledger

Read the report once end to end for sense. Then go through it again and build
a ledger. For a typical OIR this takes 20–40 minutes and it is the single
highest-value thing in the whole review.

For each assertion in §4, §5 and §6, record:

| Field | What you are asking |
|---|---|
| Line | Where it is |
| Claim | The assertion, in your own words, minimally |
| Type | Observation / Inference / Assumption |
| Evidence cited | The evidence ID, or blank |
| Does it support *this* claim? | Yes / partially / no / no evidence cited |
| Marked? | Does an inference carry likelihood + range + confidence? |

Three type definitions worth being strict about, because ICD 203 standard 3
exists precisely because they merge silently:

- **Observation** — something present in an artifact. "Authentication log
  `vpn-gw-01` records a successful session for account `svc_backup` at
  2026-07-14T02:11:07Z from 203.0.113.44 [E7]."
- **Inference** — something derived. "The session originated from
  infrastructure the actor also used for the March campaign."
- **Assumption** — something taken as given, often invisible. "The
  authentication log is complete." "Patient zero is the earliest infection we
  found." "The adversary had no insider assistance." "Initial access was the
  phishing email, because that is what we found first."

Assumptions are the ones nobody writes down. Run a Key Assumptions Check: list
the working assumptions the conclusions rest on, and for each, state what
information would demand rethinking it. The goal is not to abandon them — it
is to make them visible and to identify the observable that would break them.

**The "partially supports" row is where most real findings come from.** An
evidence item that shows a large outbound transfer supports "a large outbound
transfer occurred"; it does not support "the customer database was
exfiltrated." The gap between what the artifact shows and what the sentence
claims is the finding.

## Attribution drift

The specific pattern to hunt, because it is the one that turns a vendor's
hedged sentence into your organisation's assertion:

| Draft 1 | Draft 3 |
|---|---|
| "The vendor report associates this infrastructure with cluster X." | "The actor was X." |
| "Three of the observed TTPs appear in public reporting on X." | "TTPs are consistent with X, indicating X was responsible." |
| "One analyst noted the timing aligns with business hours in UTC+3." | "The actor operates from UTC+3." |
| "Retention for this source is 30 days." | "No activity occurred before June." |

Where prior drafts or the cited sources are available, compare. Where they are
not, the tell is a sentence that asserts a general fact but whose only
plausible basis is one specific document — especially if that document is
cited elsewhere in the report in hedged terms.

Attribution specifically. An unqualified actor name in an OIR creates two
problems beyond the analytic one: a discoverable statement the organisation
may later contradict in an 8-K or a regulator filing, and sanctions exposure
if a ransom payment follows. The safe form is always the same shape:

> Observed TTPs overlap with those publicly reported for [X] in [source, date]
> — specifically [the two or three that actually overlap]. We assess it is
> roughly even chance (45–55%) that this is the same operator; the overlapping
> TTPs are widely available. Confidence: Low.

## The six overclaim patterns

These are what to grep for by eye. The linter catches some; none of them are
reliably machine-detectable.

1. **Universal quantifiers over a population.** "All hosts were scanned." "No
   endpoints showed the indicator." Bound it: which population, from which
   inventory, as of when, with what coverage rate?
2. **Appeal to unnamed authority.** "Industry best practice", "it is well
   established", "typically attackers…". Either cite it or cut it. A
   generalisation about adversary behaviour presented as an observation about
   *this* adversary is one of the commonest ways a report acquires facts it
   never had.
3. **Proof language.** "This demonstrates", "this confirms", "this proves".
   Very few artifacts prove anything alone. Usually the honest verb is "is
   consistent with", and then the alternatives it is *also* consistent with
   need naming.
4. **Precision without provenance.** "Approximately 14,000 records." From
   what count, over what query, at what time? A number in a report that a
   regulator can ask you to reproduce and you cannot is worse than a range.
5. **Causal chains asserted from correlation.** Timeline adjacency is not
   causation, and where clock skew is unmeasured it is not even adjacency —
   NIST SP 800-92 notes that skew can make event A appear 45 seconds before
   event B when it actually happened two minutes after.
6. **Tense drift into the general present.** "The actor uses living-off-the-
   land binaries" is a claim about the actor across all time. "The actor used
   `certutil.exe` on `WKS-4471` at [time] [E12]" is a finding. Reports drift
   from the second form into the first as they are edited.

## Negative findings

"No evidence of X" is the most consequential sentence type in an OIR, because
it is what a materiality determination usually rests on, and it is the one
most often written unbounded.

An unbounded negative — "no data was exfiltrated" — dies to a single contrary
log line, and it takes the report's credibility with it. Every negative
finding needs four things:

1. **What was searched** — the specific sources.
2. **Over what window** — and the retention boundary of each source.
3. **With what query** — reproducibly.
4. **What the absence does and does not mean** — including the coverage gaps
   from §7.

> No evidence of database export was observed in `db-audit-01` and
> `db-audit-02` query logs [E31, E32] covering 2026-06-14T00:00:00Z to
> 2026-07-18T00:00:00Z. Audit logging on `db-03` was not enabled until
> 2026-07-02T14:00:00Z; activity on that host before that time cannot be
> assessed from this source.

That paragraph survives a deposition. "No data was exfiltrated" does not.

## What not to do

**Do not count hedges.** Hedge frequency varies systematically by first
language — L1-Chinese academic writers use fewer and less varied hedges than
Anglophone writers; Central and Eastern European L2 writers over-use boosters.
A hedge-frequency rule penalises analysts for their linguistic background
rather than their reasoning. Require structural marking instead: every
judgment carries a lexicon term and an inline range. That removes the confound
entirely.

**Do not use readability scores as a grade.** They are unreliable (different
tools computing the same formula disagree), invalid for the thing you care
about (they cannot see whether content answers the reader's question), and
they break on tables, IOC lists, log excerpts and timelines — which is most of
an OIR. Use them, if at all, as a screening flag on prose sections only.

**Do not rewrite for fluency.** The analyst has to be able to defend this
document. An edit that improves the prose and loosens a claim has made the
report worse in the only way that counts.
