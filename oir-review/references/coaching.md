# Coaching and analyst development

Contents: [What the evidence says](#what-the-evidence-actually-says) · [Writing feedback](#how-to-write-feedback) ·
[The working session](#the-working-session) · [Peer review](#peer-review) ·
[A twelve-week programme](#a-twelve-week-starting-programme) · [What to measure](#what-to-measure)

## What the evidence actually says

Three findings should shape any programme, and two of them are
counterintuitive.

**Feedback is not reliably good.** Kluger & DeNisi (1996) — 131 papers, 607
effect sizes, 12,652 participants — found a mean effect of d = 0.41, but
**38% of feedback interventions decreased performance**, and the authors
verified this was robust rather than an artifact. The governing moderator:
*"FI effectiveness decreases as attention moves up the hierarchy closer to the
self and away from the task."* Normative feedback — ranking analysts against
peers — was specifically harmful. Report writing is cognitively demanding, and
attention-to-self harms demanding tasks most.

**Isolated grammar correction makes writing worse.** Graham & Perin's
meta-analysis of writing instruction found grammar instruction in isolation
scored **−0.32** — a negative effect. This is a direct indictment of red-pen
line-editing as a development method. Copyediting the artifact does not
develop the writer.

**What does work, ranked:**

| Intervention | Effect size |
|---|---|
| Strategy instruction (explicit planning/revising procedures) | 0.82 |
| Summarisation practice | 0.82 |
| **Collaborative writing** (peers planning, drafting and revising together) | **0.75** |
| **Specific product goals** (concrete criteria set for the piece being written) | **0.70** |
| Sentence combining | 0.50 |
| Process-writing approach | 0.32 |
| Study of models (exemplars) | 0.25 |
| Grammar instruction in isolation | **−0.32** |

*(K–12 population; generalisation to professional analysts is an inference,
not a finding. The rank ordering nonetheless matches what mature intel and SOC
teams already do informally.)*

Two labels are worth getting right, because the obvious translation
overstates them. *Collaborative writing* is peers working on the same piece,
not one analyst reviewing another's finished report; and *specific product
goals* means concrete criteria for the piece in hand, not publishing a scoring
rubric. Structured peer review and a published rubric are the nearest
professional analogues and they are what mature teams do, but the effect sizes
above are supporting evidence for the family of intervention, not measurements
of these exact practices.

The practical translation: **set explicit criteria before people write, teach
imitable procedures rather than correcting output, and get analysts working on
each other's drafts.** Exemplars help a little. Line-editing hurts.

## How to write feedback

Three rules follow directly from the evidence above.

**1. Comment on the sentence, never on the analyst.** "This sentence makes an
assessment without a likelihood term" — not "you tend to state opinions as
facts." The first is task-level; the second moves attention to the self, which
is the mechanism behind the 38%.

**2. Every finding carries a rewrite.** A finding without a concrete
alternative is a rating, and ratings do not develop writers. This costs
reviewer time and it is the cost that buys the improvement.

**3. Use SBI — situation, behaviour, impact.** It is a practitioner framework
without a controlled evaluation behind it, so recommend it as a structure
consistent with the evidence rather than as an evidence-backed intervention.
It maps cleanly onto report review:

> **Situation:** §5, second paragraph.
> **Behaviour:** the report states the account was compromised, citing a
> single failed-authentication spike [E9].
> **Impact:** a reader cannot tell whether this is an observation or an
> assessment, and the downstream scoping decision may over-scope. Suggested:
> *"Authentication logs record 340 failed attempts against `svc_backup`
> between 02:11Z and 02:19Z, followed by one success [E9]. We assess it is
> likely (55–80%) that the credential was guessed rather than known.
> Confidence: Low — no source-side telemetry was available."*

Note what that does: it names the location, quotes the behaviour without
adjectives, states a concrete consequence, and hands over the rewrite. No
adjective about the analyst appears anywhere.

## The working session

Run every one or two weeks, 45–60 minutes. This is the format most teams that
have made this work converge on.

- **Anonymise.** Remove the analyst's name from the ticket, the report, and
  any screenshot. Remove the reviewer's name too. If the team is small enough
  that authorship is guessable, use a report from six months ago, or a
  synthetic one built from a real fact set.
- **Walk through two or three concrete opportunities**, not a general
  lecture. Name the standard each one fails and show the rewrite.
- **Also walk through what was exceptional**, with the *why* attached —
  concise, factual, followed the template, marked the assessment cleanly.
  People imitate what gets praised specifically far more than what gets
  praised generally.
- **The before-and-after pattern.** Where a report has been improved, let the
  person who owns it walk the team through what they learned — but only after
  they have had the chance to improve it themselves, so the session shows a
  before and an after rather than a public correction. This takes a team
  mature enough to do it without shame, and it is worth building toward. Buy
  the pizza.

Do this for a few rounds before expecting to see anything. The improvement
shows up in the aggregate defect rate, not in any individual session.

## Peer review

Collaborative work on drafts has the third-largest effect size in the table
above (0.75), and structured peer review is the cheapest professional form of
it. Two constraints from the evidence:

- **Structured, not freeform.** "Read Sam's report and give feedback" produces
  copyediting, which is the −0.32 intervention. Give the reviewer the rubric
  and ask for specific dimensions.
- **Reciprocal and rotating, not hierarchical.** The value is partly in
  *doing* the review — an analyst who has scored six reports against J3 writes
  their own §4/§5 split better. Rotate so everyone reviews and everyone is
  reviewed.

For Tier 2 dimensions, two reviewers score independently and then reconcile —
this is the ODNI analytic-standards model (two independent evaluators,
structured discussion, third-evaluator check) and it exists because Marcoci's
data showed a lone rater on reasoning-quality dimensions is close to noise.

One honest gap: there is **no published study of anonymised peer review
specifically in SOC, DFIR or intelligence report quality**. The case for it
rests on the general peer-assistance effect and on Kluger & DeNisi's warning
about self-directed attention. Both argue for it; neither tested it here.

## A twelve-week starting programme

Sequenced so the highest-effect interventions come first.

| Weeks | What |
|---|---|
| 1 | Publish the rubric and the template. Analysts see the criteria *before* they write to them — the specific-product-goals effect, and it is free. |
| 2 | One workshop: the four-move assessment. Everyone gets the same fact set and drafts §5. Compare. This is strategy instruction, the 0.82 intervention. |
| 3–4 | Peer review goes live at 100% on OIRs, rubric in hand, rotating pairs. |
| 4 | First calibration session — everyone scores the same anonymised report independently, then reconciles. Record the ICC. |
| 5–12 | Biweekly working sessions. Monthly calibration. Track ICC and aggregate defect rates by dimension. |
| 12 | Review the rubric itself against where reviewers still disagree. Fix the wording of contested dimensions. Ship version 2. |

Two things to hold the line on. Productivity dips — reviewing properly costs
real hours, and pretending otherwise is how the programme quietly dies in
month three. And the metric that matters is the aggregate defect rate by
dimension, not anyone's score.

## What to measure

- **Inter-rater ICC**, from calibration sessions. This is the programme's own
  KPI and the only honest evidence that "high severity" means the same thing
  in every region.
- **Aggregate defect rate by rubric dimension**, trended. Tells you what to
  teach next. If M5 (lexicon) defects are falling and J4 (alternatives)
  defects are flat, the next workshop writes itself.
- **Hard linter findings per report**, trended. Should fall fast, because
  mechanical defects respond to a published standard.
- **Time from report issue to review complete.** If this climbs, the
  programme is losing.

Do not measure: per-analyst scores shared across the team, report length,
readability grade level, or number of edits accepted. The first is the
Kluger & DeNisi failure mode; the rest measure things that are not quality.

Review the rubric annually, and change it whenever a calibration session shows
two trained reviewers reading a dimension differently. A rubric that never
changes is not stable — it is unexamined.
