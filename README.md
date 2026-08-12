# skill_oir-review

`oir-review` is a skill for Claude Code and other Claude agents. The skill
reviews, scores, and edits Operational Investigation Reports (OIRs). An OIR is
the report a security analyst writes when an investigation closes: SOC
investigation write-ups, incident reports, DFIR findings, threat-hunt reports,
and after-action summaries.

The skill applies one rule to each report: write it as if opposing counsel
will read it. In *Capital One*, *Clark Hill*, *Rutter's*, and *McMenamins*,
the court made the forensic report available to the other side. The skill
reviews for sourcing, not readability. It finds the two most important failure
modes:

- **Under-marked judgment.** Assessment written as fact.
- **Under-supported fluency.** Prose that has good style but tells more than
  the evidence shows. This mode increases when teams draft with AI.

## Repository layout

```
oir-review/
├── SKILL.md                        The skill definition and review pipeline
├── assets/
│   ├── OIR-template.md             The house report template
│   └── review-report-template.md   The output format for a review
├── references/
│   ├── standard.md                 Report structure and section content
│   ├── estimative-language.md      Likelihood, confidence, and severity terms
│   ├── sourcing-review.md          The claim ledger and attribution drift
│   ├── legal-exposure.md           Vocabulary substitutions and notification clocks
│   ├── evidence.md                 Timestamps, log citation, chain of custody
│   ├── rubric.md                   The 12-dimension rubric and calibration
│   ├── distributed-teams.md        Multi-region teams and non-native English
│   └── coaching.md                 Analyst development and peer review
└── scripts/
    ├── lint_oir.py                 Deterministic checks on a report
    ├── insert_review_tokens.py     Puts review tokens into a draft
    ├── clear_review_tokens.py      Makes sure of the read, then removes the tokens
    └── test_skill.py               Regression tests for the three scripts
```

## What the skill does

The skill works through five steps:

1. **Lint.** `lint_oir.py` finds the problems a machine can find reliably.
   The checks include lexicon compliance, likelihood terms without a numeric
   range, stacked hedges, legal-exposure vocabulary, idioms, and incorrect
   timestamps. The linter does not judge argumentation or sourcing, because
   agreement between human raters on those dimensions is low.
2. **Trace claims.** The model reads the report two times and builds a claim
   ledger. Each assertion is an observation, an inference, or an assumption.
   Each observation must point to evidence that supports the claim. Each
   inference must have a likelihood term, a numeric range, and a confidence
   statement.
3. **Score.** The rubric has 12 dimensions in two tiers. Tier 1 is
   mechanical, and one reviewer is sufficient. Tier 2 is judgment. Two
   reviewers score Tier 2 independently, then agree on a final score. The
   skill scores dimensions, not analysts.
4. **Report.** Each finding points to a line, identifies the standard, and
   gives a rewrite.
5. **Edit and plant tokens.** If the user asks for an edited draft, the skill
   makes the edits and keeps the analyst's voice. It then plants review
   tokens in the draft.

## Review tokens

An AI-edited report has good style, and reviewers use style as their test for
correct content. A clean draft gets an approval without a careful read.
Review tokens prevent this. Each token is a short incorrect clause. A
security analyst sees the error immediately, but a spell-checker does not.
There are three classes:

- **A — domain-semantic anomaly.** The clause has a technical shape, but it
  is not possible.
- **B — register breach.** An idiom in formal prose.
- **C — nonexistent citation.** The citation points to a standard that you
  cannot find.

The reviewer must report each token and its line number before the draft
clears. The scripts apply the safety rails. Tokens do not go into
fact-bearing sections. Tokens do not touch lines that hold evidentiary
content. The script only adds text, and it does not change a word of the
source.

The scripts also do not accept output names that look final or external.
They do not plant tokens two times in one file. They do not write a clean
file while a token is in the text. Do not plant tokens in a final, external,
or regulator-facing version.

## Installation

1. Copy the `oir-review` directory to `~/.claude/skills/` for personal use,
   or to `.claude/skills/` in a project.
2. Start a new Claude Code session. The skill starts when you tell Claude to
   review, edit, or grade a security investigation report.

## Scripts

Lint a report:

```bash
python3 oir-review/scripts/lint_oir.py REPORT.md --json-out REPORT-lint.json
```

Exit code 1 shows one or more hard findings. This is the usual condition for
a draft in review. Use `--lexicon phia` for the UK Probability Yardstick.

Put review tokens into an edited draft:

```bash
python3 oir-review/scripts/insert_review_tokens.py DRAFT.md \
    --out DRAFT.UNCLEARED.md --manifest tokens.json
```

Give `DRAFT.UNCLEARED.md` to the reviewer. The manifest is the answer key.
Hold it back from the reviewer.

Clear the tokens after the human read:

```bash
python3 oir-review/scripts/clear_review_tokens.py DRAFT.UNCLEARED.md \
    --manifest tokens.json --out DRAFT.CLEARED.md \
    --found RT-01@142,RT-04@318 --reviewer "Name" \
    --cleared-at 2026-07-29T18:00:00Z
```

The gate accepts a token only when the reported line number agrees with the
manifest. An ID without a line number is not proof, because the IDs are
sequential.

## Tests

```bash
python3 oir-review/scripts/test_skill.py
```

The suite covers the linter's known false positives and each safety property
of the review-token control. Run it after each change to a script.

## Requirements

- Python 3.10 or subsequent versions.
- Standard library only. No other packages. No network access.

## License

GPL-3.0. See [LICENSE](LICENSE).
