---
name: oir-review
description: Review, score, and edit Operational Investigation Reports (OIRs) written by cyber security analysts — SOC investigation write-ups, incident reports, DFIR findings, threat-hunt reports, after-action summaries. Use whenever someone asks you to review, edit, critique, QA, grade, tighten or "sanity check" a security investigation report or incident write-up; shares an analyst's draft and asks "is this good?", "would this hold up?" or "what would a regulator think?"; wants a house template, reporting standard, review rubric or peer-review process for a SOC or IR team; or mentions analyst report quality, report consistency across regions, estimative language, ICD 203, confidence versus likelihood, BLUF, or separating fact from assessment. Also use it to draft an OIR from investigation notes. Not for vulnerability-assessment, pen-test, or audit reports unless the user says the same standard applies.
---

# Reviewing Operational Investigation Reports

## What this skill is for

An Operational Investigation Report is the artifact a security analyst produces
when an investigation closes: what happened, how it was found, what the evidence
shows, what is assessed rather than known, what was affected, and what the
organisation now has to decide. It is read by people the analyst did not write
for — an executive making a materiality call, an auditor, a regulator, and
eventually, possibly, opposing counsel.

That last reader is why this is not a copyediting task. In *Capital One*,
*Clark Hill*, *Rutter's* and *McMenamins*, the forensic report was ordered
produced. So the working assumption is: **write it as though it will be
produced, because it probably will be.** A junior analyst's hunch about
attribution, phrased confidently, becomes an exhibit.

Two failure modes matter most, and they pull in opposite directions:

1. **Under-marked judgment** — assessment written as fact. "The attacker
   exfiltrated the customer database" when what the evidence shows is a large
   outbound transfer from a host that had mounted a share.
2. **Under-supported fluency** — prose that reads beautifully and asserts more
   than the evidence carries. This mode grows as teams draft with AI. Hagar et al.
   (2025) measured document-grounded LLM output — a small study, 40 responses
   — and found 30% erred; the top two error types were not invented facts but
   *editorialising about sources* and *attribution drift* — turning an
   attributed opinion into a universal statement. Those errors are invisible to
   every readability metric ever written. **Review for sourcing, not
   readability.**

Everything below serves those two problems.

## The one-line intake

Before reviewing, establish four things. If the user is present, ask. If not
(a scheduled run, an unattended session), assume the defaults, say so at the
top of the output, and continue.

| Question | Default if unattended |
|---|---|
| Is this an internal review draft, or a final/external/regulator-facing version? | internal review draft |
| Do you want an edited draft back, or findings only? | findings only |
| Is there a house template to review against? | use `assets/OIR-template.md` |
| Should review tokens be planted in the edited draft? | yes, if producing an edited draft |

**Never plant review tokens in a final, external, or regulator-facing version.**
They belong on the internal review draft only.

## The review pipeline

Work in this order. The point of the ordering is that the cheap deterministic
checks run first and clear the noise, so your attention goes to the judgment
work that only a reader can do.

### 1. Run the linter

```bash
# paths are relative to the skill directory; run from there or use absolute paths
python3 scripts/lint_oir.py REPORT.md --json-out <report>-lint.json
```

Useful flags: `--lexicon phia` if the house standard is the UK Probability
Yardstick rather than ICD 203; `--severity HARD` to see only blocking
findings; `--per-check-cap N` on very long reports. It exits **1 whenever
there is a hard finding**, which is the normal state of a draft under review —
that is a signal, not a tool failure.

This handles the checks a machine can make reliably: ICD 203 lexicon
compliance, the same-sentence confidence/likelihood prohibition, stacked
hedges, empty modifiers, legal-exposure vocabulary, idioms, non-RFC-3339
timestamps, missing sections, sentence mechanics. It deliberately does *not*
judge argumentation, sourcing adequacy or accuracy — those score at ICC 0.29
among untrained human raters (Marcoci et al. 2019), so a regex has no business
pretending otherwise.

Treat linter output as *candidate* findings. Some will be wrong in context —
a report quoting a regulator's own use of "breach" is not making a legal
conclusion. Verify each one against the surrounding text before it reaches
your output.

Where verifying a finding needs evidence you were not given — the underlying
logs, the cited vendor report, the prior draft — say so explicitly rather than
guessing in either direction. Record it as an open question in the review with
what you would need to resolve it. An unresolvable finding is a real result; a
confidently resolved one you could not actually check is the failure this
skill exists to prevent.

### 2. Trace every claim to evidence

This is the part that carries the value, and it cannot be automated. Read the
report once end to end, then go through it a second time building the claim
ledger described in `references/sourcing-review.md`. For each assertion:

- Is it an **observation** (something in an artifact), an **inference**
  (something derived from artifacts), or an **assumption** (something taken as
  given)? ICD 203 tradecraft standard 3 exists because these three get
  silently merged.
- If observation: is there an evidence reference, and does the reference
  actually support the specific claim — not a weaker or adjacent one?
- If inference: is there a likelihood term with an inline numeric range, and a
  separate confidence statement?
- If assumption: is it stated, and does the report say what happens to the
  conclusions if it is wrong?

Attribution drift is the specific pattern to hunt: a sentence that in draft 1
read "the vendor report associates this infrastructure with X" and by draft 3
reads "the actor was X." Compare against cited sources where you can.

### 3. Score against the rubric

`references/rubric.md` has a 12-dimension rubric split into two tiers, because
mixing them is what destroys inter-rater agreement:

- **Tier 1, mechanical** (6 dimensions) — high agreement, one reviewer is
  enough. M1 structure, M2 BLUF, M3 timestamps, M4 evidence hygiene,
  M5 lexicon compliance, M6 legal hygiene.
- **Tier 2, judgment** (6 dimensions) — low agreement, needs two independent
  reviewers who then reconcile. Sourcing, uncertainty, fact/assessment
  separation, alternatives, argumentation, decision value.

Score dimensions, never analysts. Kluger & DeNisi's meta-analysis (131 papers,
607 effect sizes) found feedback *decreased* performance 38% of the time, and
the moderator was attention moving from the task toward the self. No
leaderboards, no per-analyst scores visible to peers.

### 4. Write the review report

Use the structure in `assets/review-report-template.md`. Findings are anchored
to a line, state the standard they fail, and carry a concrete rewrite. A
finding without a rewrite is a rating, and ratings do not develop writers —
grammar instruction in isolation scores **−0.32** in Graham & Perin's
meta-analysis, which is to say it makes writing worse.

### 5. Produce the edited draft (only if asked)

Edit for the findings you raised, preserving the analyst's voice and every
piece of evidentiary content exactly. Then plant review tokens:

```bash
python3 scripts/insert_review_tokens.py DRAFT.md \
    --out DRAFT.UNCLEARED.md --manifest tokens.json
```

Explain what this is and why — see the section below. **Deliver
`DRAFT.UNCLEARED.md` to the reviewer; the manifest is the answer key and goes
to whoever runs the review, not to the person doing the reading.** If one
person is doing both, tell them not to open it until the read is done — it is
there to check themselves against, not to shortcut.

Say plainly that the UNCLEARED file is not a report until it has been
cleared.

### 6. Clearing

After the human read:

```bash
python3 scripts/clear_review_tokens.py DRAFT.UNCLEARED.md \
    --manifest tokens.json --out DRAFT.CLEARED.md \
    --found RT-01@142,RT-04@318 --reviewer "Name" \
    --cleared-at 2026-07-29T18:00:00Z
```

Note the `@line` syntax. Naming an ID proves nothing — the IDs are sequential
and guessable — so clearing counts a token as located only when the line
number matches the manifest within a few lines. An ID with no line is recorded
as claimed-but-unproven and does not count.

Missed tokens are the interesting output, and *where* they were missed matters
more than how many. A cluster in one section means that section was skimmed.
Class C misses (invented citations) mean citations were not checked at all.

## Review tokens: what they are and why they exist

An AI-edited report reads well, and fluency is the proxy most reviewers use for
correctness. So a clean draft gets skimmed and approved — which is the exact
outcome the review was supposed to prevent. Review tokens break the proxy.

Each token is a short clause inserted into narrative prose that is wrong in a
way a competent security analyst spots instantly and a spell-checker, grammar
tool, or model skimming for style glides straight past. Three classes:

- **A — domain-semantic anomaly.** Technically shaped, internally impossible:
  *"The host was isolated by lowering its DNS TTL to zero."* Well-formed
  jargon to a language model; nonsense to an analyst.
- **B — register breach.** An idiom dropped into formal prose: *"Bob's your
  uncle."* Doubles as practice for the idiom problem on a distributed team.
- **C — nonexistent citation.** *"This step follows NIST SP 800-61r4 §4.2."*
  Trains the sourcing reflex directly. A reviewer who checks citations finds it
  at once; a reviewer who trusts citations is exactly who this is aimed at.

This is a deliberate-error control — the same idea as proof marks in
typesetting or seeded defects in software inspection. It makes "I read it" a
checkable claim instead of a self-report. It is not a trap for the analyst and
should never be framed as one; the tokens go into the *reviewed* draft, and the
person clearing them is the reviewer.

The rails are enforced in the script, not by convention:

- **Section allowlist, not blocklist.** Tokens only enter scope, background,
  narrative, methodology, approach and next-steps prose. The bottom line,
  timeline, findings, assessments, impact, limitations, evidence register and
  every annex are off limits — a token there would corrupt the meaning of a
  finding even though it alters no character of it. A blocklist fails open;
  this fails closed, which is why the script sometimes plants fewer tokens
  than asked and says so.
- **Additive only.** No existing word, number, name, timestamp or citation is
  ever changed, and no token lands on a line carrying evidentiary content or a
  likelihood/confidence marker.
- **Refuses to double-plant.** Running it on an already-tokened file is
  rejected: a second manifest does not know about the first, and clearing with
  the second would leave the first behind.
- **Refuses unsafe outputs.** It will not overwrite its input, and it rejects
  output filenames that look final, external, or regulator-facing.
- **Clearing scans the whole bank**, not just this manifest, and refuses to
  write a clean file if any token string survives.
- **Whitespace-tolerant removal**, so re-wrapping a paragraph does not strand
  a token.

Two things the script cannot enforce, and you must:

1. It only knows what the filename looks like. Never plant on a version that
   is actually final or external, whatever it is called.
2. Never hand-remove a token. If the draft changed, clear it and re-plant.
   Hand-removal is the path by which one survives into a produced document.

And be honest with the reviewer about the limit of the control: it verifies
that the narrative prose was read. **Nothing in the fact-bearing sections is
checked by it**, and those are the sections that matter most. Say so.

## Reference files

Read the ones the task needs; don't load them all.

| File | Read it when |
|---|---|
| `references/standard.md` | Establishing or checking report structure; what belongs in which section and what must be kept *out* |
| `references/estimative-language.md` | Any question about likelihood, confidence, severity, or how to phrase an assessment |
| `references/sourcing-review.md` | Doing step 2 — the claim ledger, attribution drift, AI-overclaim |
| `references/legal-exposure.md` | Financial services, regulated industries, anything that might be produced; the substitution table and the notification clocks |
| `references/evidence.md` | Timestamps, log citation, chain of custody, retention and negative findings |
| `references/rubric.md` | Scoring; also the calibration protocol |
| `references/distributed-teams.md` | Multi-region teams, translation, non-native English, regional annexes |
| `references/coaching.md` | The user wants a development programme, peer review, or lunch-and-learn material rather than a single review |

Assets: `assets/OIR-template.md` (the house template) and
`assets/review-report-template.md` (the output format).

Scripts: `scripts/lint_oir.py`, `scripts/insert_review_tokens.py`,
`scripts/clear_review_tokens.py`, and `scripts/test_skill.py` — a regression
suite covering the linter's known false positives and every safety property
the review-token control depends on. Run it after changing any script.

## Questions the template does not ask but a review should

These come up repeatedly in real reports and are absent from most house
templates. Raise them as findings when they are missing and material.

- **Litigation hold.** When did a preservation duty attach, and what did it
  cover? "Retention expired" and "expired after the duty to preserve attached"
  are the difference between a limitation and a spoliation problem, and it is
  the first thing opposing counsel asks.
- **Distribution ledger.** Which version went to whom — carriers, brokers,
  panel counsel, auditors, regulators. *Capital One* turned substantially on
  who received the report. A handling legend records intent; a ledger records
  fact.
- **Sanctions screening.** Where extortion is in play, the OFAC screening
  record has to exist before any payment decision, and NYDFS's 24-hour
  extortion clock needs something to feed it.
- **Consistency with what has already been said.** Compare against filings,
  customer notices and regulator submissions already made. A report that
  contradicts an issued 8-K is a problem the report created.
- **Non-US regulators.** NIS2 (24-hour early warning, 72-hour notification,
  one-month final report), DORA, UK ICO, CERT-In's 6 hours, Australia's SOCI
  12/72, card-brand PFI obligations.
- **Third-party and supply-chain scope.** Both NYDFS §500.17 and Reg S-P key
  on service-provider events.
- **Human sources.** Interviews and employee statements carry much of the risk
  in a real investigation and appear in no evidence register. They need the
  same treatment: who, when, what was asked, and a source descriptor.
- **Data minimisation.** Sample records, credentials, tokens and personal data
  pasted into a report that will be produced are their own exposure. Reference,
  do not paste.
- **Response actions taken.** The template records what the adversary did;
  what the responders did — containment, eradication, credential rotation,
  with times — belongs in the record too.

## Things that are easy to get wrong

**Do not police hedging by frequency.** Counting hedges systematically
penalises analysts whose first language is not English — L1-Chinese writers
under-hedge relative to Anglophone norms, Central European writers over-boost.
The fix is structural, not stylistic: require every judgment to carry a term
from the fixed lexicon plus an inline range. That removes the L1 confound
entirely.

**Do not use readability scores as a grade.** They cannot see whether the
content answers the reader's question, they break on tables and log excerpts,
and AI-drafted prose scores *better* precisely while it drifts attribution.
Use them as a screening flag on prose sections only, never as a number in the
output.

**Do not use stylometric AI detection.** "Delve", em-dash density and uniform
sentence length false-positive hard on non-native speakers and on anyone using
translation tools. The defensible test is claim-to-source traceability.

**Do not let one reviewer produce a final score on the judgment dimensions.**
Marcoci et al. found the ICD 203 criteria essentially unreliable among
untrained raters (ICC 0.29), and meaningfully better after group calibration.
Their conclusion was blunt: no assessment should be produced by a lone
analyst. (See `references/rubric.md` for the caveats — the improvement is real
but the confidence intervals are wide.)

**Do not rewrite the analyst's voice.** Edit for the findings you raised.
Wholesale rewriting produces a document the analyst cannot defend in a
deposition, and teaches them nothing.

**Do not move remediation recommendations into the report to be helpful.**
*Clark Hill* singled out "pages of specific recommendations on how the Firm
should tighten its cybersecurity" as proof the document was a business artifact
rather than legal work product. Recommendations belong in a separate document.

## Output

Default deliverables:

1. `<report>-review.md` — the review report, following
   `assets/review-report-template.md`
2. `<report>-lint.json` — raw linter findings, for the record
3. If an edited draft was requested: `<report>.UNCLEARED.md` for the reviewer,
   and `tokens.json` for whoever runs the review

Send files with SendUserFile as they are produced. Lead the response with the
verdict and the count of hard findings — the same BLUF discipline the report
itself is being held to.
