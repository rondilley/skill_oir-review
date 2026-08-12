# Distributed teams: language, culture, and one standard

Contents: [The real problem](#the-real-problem-is-not-grammar) · [Numbers survive translation](#numbers-survive-translation-adjectives-do-not) ·
[What not to build](#what-not-to-build) · [Language policy](#language-policy) ·
[Handoffs](#shift-handoffs) · [Regional annexes](#regional-annexes) · [Rollout](#rollout)

## The real problem is not grammar

The instinct on a globally distributed team is to treat report inconsistency
as an English-proficiency problem and solve it with proficiency testing and
writing training. That misreads the failure.

Analysts can all write clean English and still mean different things. Kent
documented it inside a single US organisation in 1964: he read "serious
possibility" as 65:35, and colleagues on the same estimative board gave
answers spanning 20:80 to 80:20. His verdict was "we are in disarray", and
that was one office, one language, one building. Photo-interpreters' "possible"
mapped to his "probable"; another shop's "firm" meant 90–95%, shifting every
band below it.

Now add languages. Budescu et al. (2014) surveyed 10,792 people across 24
countries and 17 languages on the IPCC's probability terms:

- Consistency with the intended ranges was **27%** using verbal terms alone.
- The dominant failure was **regression toward 50%** — "very likely" (official
  >90%) was read as spanning 51–86%; "very unlikely" (official <1%) as 9–30%.
- **The extremes are worst.** Per-term consistency: *very unlikely* 16%,
  *unlikely* 32%, *likely* 43%, *very likely* 48%. The terms analysts most
  want for high-stakes calls are the ones readers get most wrong.

Harris et al. (2013) compared Chinese and UK readers on the same terms and
found Chinese interpretations diverged further from the intended ranges and
showed greater variance.

So the problem is not that analysts write badly. It is that verbal probability
does not transmit — within one language, and worse across several.

## Numbers survive translation, adjectives do not

The fix is boring and it works.

Budescu: adding a numeric range lifted consistency from **27% to 40%**,
uniformly across all 24 countries — no cultural moderator. It also *homogenised
across languages*: national samples clustered more tightly under
verbal+numeric than under verbal alone. One intervention, two problems.

Wintle et al. (2019) then tested where the number has to go, using the ICD 203
lexicon:

| Format | Best estimate in the intended range | Interval overlaps it |
|---|---|---|
| No guidance | 59% | 32% |
| Lexicon in a reference table | 64% | 39% |
| Hover tooltip | 65% | 40% |
| **Number inline in the sentence** | **82%** | **66%** |

Publishing the lexicon in the style guide moves the needle by about five
points. Putting the number in the sentence moves it by more than twenty. That
is the single most useful operational finding for a distributed team, and it
costs nothing. (Dhami & Mandel have contested Wintle's agreement measure; the
ranking of the four formats is not contested.)

Two corollaries:

- **Negatively-worded terms are worse.** Interpretation spread roughly doubles
  under negation (SDs: *very unlikely* 21.1 and *unlikely* 20.7, versus
  *likely* 13.0 and *very likely* 12.9). Where a judgment can be phrased
  positively, phrase it positively.
- **UTC and RFC 3339 are the same move applied to time.** `07/29/2026` is not
  ambiguous — it is *differently* unambiguous depending on the reader. See
  `evidence.md`.

## What not to build

**Do not build a per-nationality communication model.** Hall's high-context /
low-context framework is ubiquitous in management training and empirically
weak — Kittler, Rygl & Mackinnon's systematic review found the country
classifications rest on "seemingly less-than-adequate evidence" and are
"flawed or, at best, very limited", with mixed and often contradictory
findings. A rubric rule that says "analysts from country X will be indirect"
is both unfair and wrong. Use it at most as a soft reminder that implicitness
varies between people; never as a classifier.

**Do not police hedging by frequency.** Hedging norms vary systematically by
first language — L1-Chinese academic English uses fewer and less varied
hedges than Anglophone writing; Central and Eastern European L2 writers
over-use boosters. A hedge-count heuristic penalises analysts for their
linguistic background rather than their reasoning. Make uncertainty
*structural* instead: every judgment carries a lexicon term and an inline
range. That removes the confound entirely, and it is the same rule that fixes
comprehension.

**Do not use stylometric AI detection.** Non-native English writers and
translation-tool users produce exactly the surface features an AI detector
keys on: elevated formality, uniform sentence length, heavy connective use.
Trace claims to sources instead.

**Do not assume proficiency testing solves the analytic problem.** It solves a
different, real problem — comprehension of the source material and ability to
be understood in a handoff — and it is a legitimate requirement to set, with
recognised international proficiency standards and a stated transition period.
But two analysts who both pass a C1 exam can still disagree about "likely".

## Language policy

The workable pattern, seen in multinationals that have made this work, is to
separate **local work** from **cross-timezone or cross-organisational work**.
Local investigations can be conducted and documented locally. Anything that
crosses a shift boundary, an organisational boundary, or goes to a regulator
runs in the common language.

Whatever that language is — English is the common default, but standardising
on French, Mandarin or anything else works if two conditions hold: the
requirement is clear to everyone in advance with a planned transition, and
proficiency is measured against a recognised international standard rather
than a manager's impression.

Then, whatever the language:

- **Idioms are banned in reports.** Not discouraged — banned. "Bob's your
  uncle", "low-hanging fruit", "smoking gun", "dodged a bullet", "boil the
  ocean". They survive spell-check, break machine translation, and read as
  unserious to a regulator. The linter flags a starter list; extend it with
  whatever the team actually says.
- **Phrasal verbs get literal replacements where a plain verb exists.** "Was
  brought about by" → "caused". "Ran into" → "encountered". Phrasal verbs are
  the single hardest English construction for non-native readers and the
  hardest for translation tools.
- **One idea per sentence.** This is the Federal Plain Language Guidelines'
  rule and it is better grounded and more actionable than any word count.
  (The famous "8 words = 100% comprehension, 43 words = under 10%" figures
  attributed to the American Press Institute have no traceable primary source
  — do not put them in a style guide.) Flag sentences over 30 words and any
  sentence carrying more than one analytic judgment; do not enforce an
  average.

## Shift handoffs

Follow-the-sun operations create a specific report failure: the interim
written at end-of-shift in one region is the input to the next region's
investigation, and its unmarked assumptions become that region's facts.

Three things make handoff reports survivable:

1. **The four-move assessment** (see `estimative-language.md`) — judgment,
   confidence with driver, alternatives, what would change it. The fourth move
   is what tells the incoming shift what to look for.
2. **An explicit "open questions" block** at the end of every interim, naming
   what the outgoing shift would have done next.
3. **Explicit supersession** when the incoming shift changes a judgment —
   state the old judgment, the new one, and the evidence that moved it. This
   is ICD 203 standard 7, and on a distributed team it is also the only
   mechanism that stops a wrong early call propagating around the globe once
   a day.

## Regional annexes

One template globally; annexes by jurisdiction, each with an applicability
line at the top: *"Complete only if EU or UK data subjects are in scope."*

The failure mode to avoid is stuffing every jurisdiction's fields into the
core template — you get a twelve-page form that nobody completes and that
teaches analysts the form is optional. The other failure mode is letting each
region maintain its own template, which is how "high severity" ends up meaning
two different things.

Be explicit that some sections exist for reasons a given region will not find
obvious. An analyst in Singapore has no reason to know why a US
financial-services report needs a Reg S-P sensitive-customer-information
field, and an analyst in the US has no reason to know the GDPR 72-hour clock
runs from awareness. Say why the field is there, in the template, next to the
field.

## Rollout

Ship version 1 from the best template in use today, not from a blank page. A
standard that arrives as a replacement gets resisted; one that arrives as
three additions to the form people already fill in gets adopted. Note what is
missing and what is extra, be explicit that this is version 1, commit to an
annual review, and change it when calibration sessions show a dimension two
trained reviewers read differently.
