# The rubric

Contents: [Why two tiers](#why-two-tiers) · [Tier 1: mechanical](#tier-1-mechanical-one-reviewer) ·
[Tier 2: judgment](#tier-2-judgment-two-reviewers) · [Scoring and thresholds](#scoring-and-thresholds) ·
[Calibration](#calibration) · [QA sampling](#qa-sampling-rates)

## Why two tiers

Most report-quality rubrics fail because they mix two kinds of question and
then report one number.

Marcoci, Vercammen & Burgman (2019) ran the first empirical test of the ICD
203 tradecraft standards as a rating instrument. Untrained raters produced an
intraclass correlation of **0.294** (equal weights) and roughly **zero**
weighted — essentially unreliable. After a 45-minute group calibration the
figure rose to **0.612**. Their conclusion: *"no assessment should be produced
by a lone analyst."*

Read that improvement with its caveats, because they are substantial: the
0.612 carries a 95% confidence interval of [−0.101, 0.894], which spans zero;
the comparable two-rater figure was 0.473; the second experiment deliberately
used the reports that had scored *worst* for reliability in the first, which
invites regression to the mean; the raters were postgraduate students rating
reasoning reports, not analysts rating intelligence products; and one
criterion was dropped from the instrument. The safe reading is that the ICD
203 criteria are unreliable without calibration and meaningfully better with
it — not that 45 minutes reliably doubles anything.

The contrast with clinical documentation rubrics is suggestive rather than
decisive. The PDQI-9 reports an ICC of 0.83, but that is an average-measures
figure across many raters and is not like-for-like with Marcoci's. What the
pair does support is a design intuition worth acting on: PDQI-9's dimensions
are properties of the *document*, ICD 203's are properties of the *reasoning*,
and document properties are the easier thing to rate consistently.

So this rubric splits them. Tier 1 is mechanical, high-agreement, one
reviewer. Tier 2 is judgment, low-agreement, two independent reviewers who
then reconcile — mirroring how ODNI's own analytic standards office works
(two independent evaluators, structured discussion, third-evaluator check).

Reporting one blended number would hide exactly the distinction that makes the
scores usable.

## Tier 1: mechanical (one reviewer)

Scored 0–3: **0** absent · **1** present but deficient · **2** adequate ·
**3** exemplary.

| # | Dimension | 3 looks like |
|---|---|---|
| M1 | **Structure** | All eight sections present, in order, with regional annexes marked for applicability. Remediation is elsewhere. |
| M2 | **BLUF** | Severity, one-sentence what-happened, determination status, decision requested, and report version — all within the first 150 words. |
| M3 | **Timestamps** | Every body timestamp RFC 3339 UTC. Original offsets preserved in the register. Skew measured and stated, or its absence noted in §7. |
| M4 | **Evidence hygiene** | Every finding carries an evidence ID. Register has source, version, query, retrieval time, hash, retention, custodian. SOP deviations disclosed. |
| M5 | **Lexicon compliance** | Every judgment carries a term from the agreed row with an inline numeric range. No confidence/likelihood in one sentence. No stacked hedges. Severity taxonomy named. |
| M6 | **Legal hygiene** | No "breach" as a conclusion, no fault or adequacy language, no counterfactuals, no unbounded absolutes, no unqualified attribution, no recommendations. Determinations timestamped. |

`scripts/lint_oir.py` produces candidate findings for M3, M5 and M6 and
partial coverage of M1 and M2. Verify each in context before scoring — the
linter has no idea that a report quoting a regulator's own use of "breach" is
not making a legal conclusion.

## Tier 2: judgment (two reviewers)

Two reviewers score independently, then reconcile. Where they differ by more
than one point, the reconciliation discussion is the useful artifact, not the
final number.

| # | Dimension | 3 looks like |
|---|---|---|
| J1 | **Sourcing adequacy** | Each cited artifact actually supports the specific claim made. Source quality is characterised, not just listed. A source summary statement covers strengths, weaknesses, and which sources carry the key judgments. |
| J2 | **Uncertainty** | Likelihood and confidence both expressed, separately, with confidence tied to a stated driver. Causes of uncertainty named. |
| J3 | **Fact / assessment separation** | Observations, inferences and assumptions are structurally distinct. Linchpin assumptions are stated, with what happens to conclusions if they are wrong. |
| J4 | **Alternatives** | Plausible alternative explanations identified and assessed. What evidence discriminates between them is stated. Indicators that would change the assessment are given. |
| J5 | **Argumentation** | The main message is up front, the report is internally consistent, contrary information is acknowledged, and the chain from artifact to conclusion is followable by someone who was not there. |
| J6 | **Decision value** | A reader can make the decision the report exists to support — materiality, notification, escalation, closure — without asking a follow-up question. Impact bounded by what was searched. |

Two known-hard cases, flagged because calibration does *not* reliably fix
them (Marcoci found J1, J5 and accuracy stayed contested even after training):

*(Marcoci found that calibration improved agreement on the uncertainty,
alternatives and implications criteria but left source description, clear
argumentation and accuracy contested. J1, J5 and J6 below are this skill's own
dimensions, but they cover the same ground, so expect the same pattern.)*

- **J1** disagreements are usually about how much corroboration counts as
  corroboration. Resolve by naming the standard in the house guide, not by
  arguing case by case.
- **J5** disagreements are usually stylistic preferences wearing a rigour
  costume. If a reviewer cannot point to a specific step in the chain that
  does not follow, the score is not a J5 finding.

## Scoring and thresholds

Report the tiers separately. Equal weights within each tier — Marcoci found
equal weights outperformed weighted scoring on both reliability and validity,
and there is no literature validating any particular weighting. If you weight,
you own the burden of validating the weights.

- **Tier 1: /18.** Below 12, or any M-dimension at 0, means the report is not
  ready for the judgment review — send it back with the mechanical findings
  first. Mechanical defects generate noise that swamps the real reading.
- **Tier 2: /18.** Below 12 means a rework, not a copy-edit.
- **Any HARD linter finding that survives verification blocks release**,
  regardless of score.

Score dimensions, never analysts. Kluger & DeNisi's meta-analysis — 131
papers, 607 effect sizes, 12,652 participants — found a mean effect of
d = 0.41 but with **38% of feedback interventions decreasing performance**,
and the governing moderator was attention moving away from the task toward the
self. Normative feedback (ranking people against peers) was specifically
harmful. So: no leaderboards, no per-analyst dashboards, no scores visible
across the team. Aggregate trends across the team are fine and useful;
per-person comparison is not.

## Calibration

The cheapest high-leverage intervention available, and the only one in this
document with a measured effect behind it: in Marcoci's study a 45-minute
calibration moved ICC from 0.29 to 0.61, with the caveats noted above.

Monthly, 45–60 minutes:

1. Pick one real report. Anonymise it — remove the analyst's name, the
   reviewer's name, and enough case detail that authorship is not obvious.
2. Every reviewer scores it independently, in advance, without discussion.
3. Reveal all scores at once. Spend the session on the dimensions where the
   spread is widest, not on the ones everyone agreed on.
4. Where a disagreement turns out to be about what a dimension means, fix the
   rubric's wording that day. Do not resolve it by fiat and move on — a
   dimension two trained reviewers read differently will keep producing noise.
5. Track ICC over time. It is the programme's own KPI, and it is the only
   honest evidence that the standard is being applied consistently across
   regions.

Reviewers who have not attended a calibration session in the last quarter
should not be the sole reviewer on a Tier 2 assessment.

## QA sampling rates

Sample rate should scale inversely with volume and directly with impact. The
one published SOC model (Expel) treats it as a manufacturing inspection
problem under ISO 2859-1, sampling daily and covering both day and night
shifts:

| Work item | Volume/day | Sample | Rate |
|---|---|---|---|
| Alerts | ~500 | 20 | 4% |
| Investigations | ~30 | 5 | 17% |
| Incidents | 2–3 | 3 | 100% |

For OIRs specifically: **100% review is the norm** — they are incident-grade
by definition and there are few enough of them. Sampling belongs to the
high-volume, low-stakes end.

Two operational notes. Sample across shifts and regions deliberately, or the
sample silently becomes "reports written during the reviewer's working hours",
which on a follow-the-sun team means one region gets reviewed and two do not.
And use pass/fail against a defect threshold for high-volume items rather than
a continuous score — continuous scores on 500 alerts a day generate precision
nobody acts on.
