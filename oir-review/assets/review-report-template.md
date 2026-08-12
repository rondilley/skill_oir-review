# Review — [Report title / case ID]

**Reviewed:** YYYY-MM-DDTHH:MM:SSZ · **Reviewer:** [name/role] · **Report version:** [vN]
**Review type:** Tier 1 only | Tier 1 + Tier 2 (single reviewer) | Tier 1 + Tier 2 (two reviewers, reconciled)

> Findings below are anchored to the document, name the standard they fail,
> and carry a rewrite. They comment on sentences, not on the analyst.

---

## Verdict

**[Ready to issue | Ready after mechanical fixes | Rework required]**

[Two or three sentences. What is the report's strongest quality, what is the
single thing that most needs to change, and can it be issued.]

- **Blocking findings:** [n]
- **Tier 1 (mechanical): [n]/18** — [one line]
- **Tier 2 (judgment): [n]/18** — [one line, or "not scored — single reviewer"]

*Intake assumptions:* [only if the review ran unattended — state what was
assumed about draft status, house template, and whether an edited draft was
wanted.]

---

## Blocking findings

*Must be resolved before issue. A hard finding blocks release regardless of
score.*

### B1 — [short title] · §[section], line [n] · [standard: e.g. ICD 203 §D.6.e(2)(b)]

**Current:**
> [quote]

**Problem:** [What is wrong, and what it costs — which reader is misled, or
which exposure it creates. One or two sentences.]

**Rewrite:**
> [concrete replacement]

---

## Findings

*Should be resolved. Grouped by rubric dimension so the pattern is visible.*

### [Dimension — e.g. J3 Fact / assessment separation]

**F1 — §[section], line [n]**

**Current:**
> [quote]

**Problem:** [one or two sentences]

**Rewrite:**
> [concrete replacement]

---

## Notes

*Optional improvements, style, or things worth discussing. No action required.*

- §[n] — [note]

---

## Scores

### Tier 1 — mechanical (one reviewer)

| # | Dimension | Score | Note |
|---|---|---|---|
| M1 | Structure | /3 | |
| M2 | BLUF | /3 | |
| M3 | Timestamps | /3 | |
| M4 | Evidence hygiene | /3 | |
| M5 | Lexicon compliance | /3 | |
| M6 | Legal hygiene | /3 | |
| | **Total** | **/18** | |

### Tier 2 — judgment (two reviewers, reconciled)

| # | Dimension | R1 | R2 | Agreed | Note |
|---|---|---|---|---|---|
| J1 | Sourcing adequacy | /3 | /3 | /3 | |
| J2 | Uncertainty | /3 | /3 | /3 | |
| J3 | Fact / assessment separation | /3 | /3 | /3 | |
| J4 | Alternatives | /3 | /3 | /3 | |
| J5 | Argumentation | /3 | /3 | /3 | |
| J6 | Decision value | /3 | /3 | /3 | |
| | **Total** | | | **/18** | |

**Reconciliation notes:** [Where the two reviewers differed by more than one
point, what the disagreement was about. If it turned out to be about what a
dimension *means*, that is a rubric defect — flag it for the next calibration
session.]

---

## Open questions

*Findings that could not be resolved because the underlying evidence was not
available to the reviewer. Say what would resolve each one.*

- [finding] — needs [artifact / prior draft / cited source]

## Claim ledger

*The evidence trace. Rows where the evidence only partially supports the claim
are where most findings come from.*

| Line | Claim | Type | Evidence | Supports this claim? | Marked? |
|---|---|---|---|---|---|
| | | Obs/Inf/Asm | [E] | yes / partial / no / none cited | y/n |

**Unstated assumptions identified:** [the ones the report rests on but does
not name]

---

## What was strong

*Specific, with the why attached. This is the material for the next
working session, and people imitate specific praise far more than general
praise.*

- §[n] — [what was done well and why it worked]

---

## Deliverables

- Edited draft: `[file].UNCLEARED.md` — **contains [n] review tokens; not a
  report until cleared**
- Token manifest: `tokens.json` — the answer key. It goes to whoever runs the
  review, not to the reader. If that is the same person, do not open it until
  the read is finished.
- Raw linter findings: `[file]-lint.json`

**To clear:** read the whole draft, list every inserted clause you find, then

```bash
python3 scripts/clear_review_tokens.py [file].UNCLEARED.md \
  --manifest tokens.json --out [file].CLEARED.md \
  --found RT-01@142,RT-03@318 --reviewer "Name" \
  --cleared-at YYYY-MM-DDTHH:MM:SSZ
```

The `@line` is the proof — an ID on its own does not count. Tokens are never
planted in the findings, timeline, assessments, impact, limitations, evidence
register or annexes, so **clearing verifies the narrative sections only**.
Those other sections need a deliberate read of their own.
