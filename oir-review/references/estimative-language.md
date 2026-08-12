# Estimative language: likelihood, confidence, severity

Contents: [Three different axes](#three-different-axes) · [The likelihood lexicon](#the-likelihood-lexicon-icd-203) ·
[Inline numbers](#why-the-number-has-to-be-in-the-sentence) · [Confidence](#confidence) ·
[The separation rule](#the-separation-rule) · [Severity](#severity) ·
[Source grading](#source-reliability-and-credibility) · [The four-move assessment](#the-four-move-assessment) ·
[Common conflations](#common-conflations)

Do not write a house lexicon. ICD 203 already exists, it is about eight pages,
and it does the hard part: it separates likelihood from confidence, forbids
mixing them in one sentence, and ties the estimative words to numeric ranges.
Lift the table.

## Three different axes

| Axis | Question | Scale | About |
|---|---|---|---|
| **Likelihood** | How probable is it that this is true / that this happened? | 7 tiers, 01–99% | the world |
| **Confidence** | How good is the evidence and reasoning behind that estimate? | High / Moderate / Low | the analysis |
| **Severity** | If true, how bad is it? | house taxonomy | the consequence |

These are independent. "We are highly confident this was almost certainly not
a nation-state actor" is perfectly coherent — high confidence in a
low-likelihood judgment — and it is also an ICD 203 violation as written,
because it puts both in one sentence.

## The likelihood lexicon (ICD 203)

ICD 203 §D.6.e(2)(a) gives two interchangeable rows. Pick one row and stay in
it; mixing rows requires an explicit disclaimer that the two sets mean the
same thing.

| | | | | | | |
|---|---|---|---|---|---|---|
| almost no chance | very unlikely | unlikely | roughly even chance | likely | very likely | almost certain(ly) |
| remote | highly improbable | improbable | roughly even odds | probable | highly probable | nearly certain |
| **01–05%** | **05–20%** | **20–45%** | **45–55%** | **55–80%** | **80–95%** | **95–99%** |

Two things to know about that table. The bands **overlap at every boundary**
(05, 20, 45, 55, 80, 95 each appear twice) — that is in the original, not a
transcription error, so a boundary case is a judgment call and not a rule
violation. And 0% and 100% are unassigned, deliberately: intelligence does
not deal in certainty, and neither does an investigation.

For operational reports **use row 1**. It is plainer English and it survives
translation better.

*(The UK PHIA Probability Yardstick is an equally defensible choice and has
deliberate gaps between bands, which some teams prefer because it stops
arguments about boundary cases. Do not run both.)*

## Why the number has to be in the sentence

This is the single most actionable finding in the research, and it contradicts
what most style guides do.

Wintle et al. (2019, *PLOS ONE*, n=924) tested the ICD 203 lexicon in four
presentation formats and measured how often readers landed inside the intended
range:

| Format | Best estimate falls inside the intended range | Reader's whole interval overlaps it |
|---|---|---|
| No guidance | 59% | 32% |
| Lexicon in a lookup table | 64% | 39% |
| Hover tooltip | 65% | 40% |
| **Number inline in the sentence** | **82%** | **66%** |

Two measures because the paper reports two: whether the reader's single best
guess lands in the band, and the stricter test of whether their whole stated
interval overlaps it. Both say the same thing — inlining the number is worth
roughly 20 points, and a lookup table is worth about 5.

A glossary at the back of the report is worth a few points. The number in the
sentence is worth four times as much. (Dhami & Mandel have disputed Wintle's
agreement measure; the direction of the result is not in dispute.)

Budescu et al. (2014) found the same thing across 24 countries and 17
languages (n=10,792): consistency with the intended range rose from 27% to
40% when a numeric range accompanied the verbal term, and — importantly for a
distributed team — the improvement was uniform across cultures. National
samples also clustered *more tightly* under verbal+numeric, meaning the number
does double duty: it fixes comprehension and it fixes cross-language drift at
the same time.

So the house rule is: **every likelihood term carries its range, in
parentheses, in the sentence.**

> We assess it is likely (55–80%) that initial access occurred through the
> VPN account rather than the phishing message.

## Confidence

ICD 203 requires confidence to be expressed but does not define the tiers. The
canonical definitions come from the IC's estimative-language annex, and the
FIRST CTI-SIG publishes an equivalent set for cyber:

- **High** — good quality information, from multiple independent collection
  capabilities, supporting a clear judgment.
- **Moderate** — credibly sourced and plausible, but not sufficiently
  corroborated, or open to several interpretations.
- **Low** — fragmentary, poorly corroborated, or from sources of uncertain
  reliability.

Two traps:

**Confidence is about the evidence base, not about how sure the analyst
feels.** A report that says "we are confident" without saying what makes the
source base strong fails ICD 203 standards 1 and 2 at once. Write the driver:
"Confidence: Moderate — the finding rests on a single telemetry source, and
the host was reimaged before acquisition."

**Confidence is not inflated by source count.** Three threat-intel vendors
reporting the same indicator usually trace to one original observation.
Independence, not count.

## The separation rule

ICD 203 §D.6.e(2)(b), verbatim:

> "To avoid confusion, products that express an analyst's confidence in an
> assessment or judgment using a 'confidence level' (e.g., 'high confidence')
> must not combine a confidence level and a degree of likelihood, which refers
> to an event or development, in the same sentence."

This is a hard prohibition and it is trivially checkable, which makes it the
best single lint rule available. The linter flags it as HARD.

- ✗ "We have high confidence that data exfiltration is likely."
- ✓ "We assess it is likely (55–80%) that data was exfiltrated. Confidence:
  Moderate — the assessment rests on netflow volume alone; no content
  inspection was available for the egress path."

**Stacked hedges** are the related sin. Kent (1964, fn. 9) pointed out that
two hedges multiply, and that the result is not what the writer meant: "we
believe" (75%) doubled with "likely" (75%) yields odds *worse than* 3 to 2,
where the writer intended 3 to 1. "May well", "could potentially", "possibly may", "we believe it is
likely" — keep one operative term and delete the rest.

**Empty modifiers** are the third. The CIA DI Style Manual: *"Do not weaken
judgments supported by direct evidence by inserting words like apparently,
evidently, seemingly, purportedly. Conversely, you cannot strengthen judgments
based on weak evidence by using words like obviously, undoubtedly, clearly.
These adverbs are an instance of modifiers that do little or no work."*

And unmodified "reportedly" — Kent again — *"carries no evaluative weight
whatsoever."*

## Severity

Severity is a house choice; what matters is that low and critical mean the
same thing in Singapore as they do in New Jersey. Three defensible public
options:

**NIST SP 800-61r2 categorisation** (r3 dropped these tables; r2 remains
citable, and it is still the best field-level scheme). Three independent axes,
which is its virtue — it stops severity collapsing into one adjective:

- *Functional impact*: None / Low (efficiency lost) / Medium (critical service
  lost for a subset of users) / High (critical service lost for all users)
- *Information impact*: None / Privacy breach / Proprietary breach / Integrity
  loss — explicitly not mutually exclusive
- *Recoverability*: Regular / Supplemented / Extended / Not recoverable

**CISA NCISS** — the National Cyber Incident Scoring System, whose priority
levels run Emergency (black), Severe (red), High (orange), Medium (yellow),
Low (green), Baseline-Minor (blue), Baseline-Negligible (white). Scored as a
weighted mean across functional impact, observed activity, location of
activity, actor characterisation, information impact, recoverability,
cross-sector dependency and potential impact, with weights set by the
organisation's own risk process. *Do not hardcode numeric score bands from
memory — pull the current NCISS PDF.*

The related but distinct **Cyber Incident Severity Schema** (from the 2016
PPD-41 lineage) uses six levels, 0 through 5. Do not conflate the two, and
check which one a counterpart means when they say "a Level 3".

**CIS/MS-ISAC Alert Level** — Green/Blue/Yellow/Orange/Red, a simpler
organisational posture scale.

**CVSS is not an incident severity scale.** Scoring an incident with CVSS is a
category error: CVSS rates the intrinsic severity of a *vulnerability*. Use
CVSS for the exploited vulnerability, and an incident taxonomy for the
incident.

Whichever is chosen, name it in the report: "Severity: High (NIST 800-61r2
functional impact: Medium; information impact: Proprietary breach;
recoverability: Supplemented)."

## Source reliability and credibility

If the team grades sources, the Admiralty / NATO matrix is the standard: A–F
for source reliability, 1–6 for information credibility.

| | Reliability | | Credibility |
|---|---|---|---|
| A | Completely reliable | 1 | Confirmed by other independent sources |
| B | Usually reliable | 2 | Probably true — not confirmed, logical, consistent |
| C | Fairly reliable | 3 | Possibly true — reasonably logical, partly consistent |
| D | Not usually reliable | 4 | Doubtful — possible but not logical, uncorroborated |
| E | Unreliable | 5 | Improbable — contradicted by other information |
| F | Cannot be judged | 6 | Truth cannot be judged |

The known failure mode is worth flagging in review. The observation that
encoders in practice assign codes **along the diagonal** — A1, B2, C3 —
collapsing two supposedly independent dimensions into one, goes back to Baker
et al. (1968) and is recounted in Kelly, Budescu, Dhami & Mandel (2025). If
every source in a report is graded on the diagonal, ask whether the two axes
are being assessed independently at all; a source's track record and the
corroboration of a particular claim are different questions, and they can
legitimately diverge (an unreliable source reporting something independently
corroborated; a reliable source reporting something implausible). Note that
Kelly et al.'s own finding is more nuanced — moderate rather than zero
consistency between the two axes produced the most reliable judgments — so
treat systematic diagonal grading as a prompt to check, not as a defect in
itself.

Note that ICD 206 itself prescribes **no graded scale**. It requires a
*narrative* source descriptor covering accuracy and completeness, possible
denial and deception, age and currency, technical elements of collection,
source access, validation, motivation, possible bias, and expertise. For most
SOC teams a short narrative descriptor plus a source summary statement beats
a letter-number code that will drift to the diagonal within a quarter.

## The four-move assessment

Every assessment in §5 makes four moves. Missing any one of them is a finding.

1. **The judgment, with likelihood and inline range.**
   *"We assess it is likely (55–80%) that the actor obtained the VPN
   credentials through the March infostealer infection rather than through
   the phishing campaign."*
2. **Confidence, in its own sentence, with its driver.**
   *"Confidence: Moderate. The credential-source judgment rests on a single
   commercial stealer-log dataset [E22]; we have no independent
   corroboration."*
3. **Alternatives, and what discriminates.**
   *"The alternative — credential reuse from a prior unrelated breach —
   remains open. Recovery of the workstation's browser credential store,
   destroyed at reimage on 2026-07-16, would have discriminated between
   these."*
4. **What would change it.**
   *"This assessment would change if authentication logs show VPN access from
   the same source ASN before the infostealer infection date."*

Four sentences. That single pattern satisfies ICD 203 tradecraft standards 2,
3, 4 and 7 at once, and it is the thing most worth teaching in a
lunch-and-learn because it is imitable.

## Common conflations

**Confidence used to mean probability.** Friedman & Zeckhauser found the 2007
Iran NIE used "confidence" 19 times to convey probability rather than to
qualify one. The reader cannot then tell whether a judgment means 10% or 40%.

**"We assess" / "we judge" substituting for an odds word.** Kesselman's
analysis of NIE key judgments across 58 years found exactly this drift —
"estimate" and "believe" collapsing, "assess" and "judge" rising — and
concluded there was "a real lack of consistency in the way analysts have been
conveying assessments." An epistemic verb is not a probability. Kent called it
"say something without saying it, in short fudge it."

**Severity smuggled in as likelihood.** "High risk of data exfiltration"
usually means the *impact* would be high, not that exfiltration is probable.
Risk is likelihood × impact; collapsing them double-counts one term and drops
the other.

**"Will".** Kesselman found "will" was by far the most common estimative word
in NIEs — over 700 occurrences — and it asserts certainty that investigation
never has. In an OIR, "the actor will return" is not a finding.
