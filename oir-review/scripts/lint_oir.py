#!/usr/bin/env python3
"""
lint_oir.py — deterministic checks for Operational Investigation Reports.

This script handles ONLY the checks that a machine can make reliably: lexicon
compliance, sentence mechanics, timestamp format, banned-phrase detection.
It deliberately does NOT try to judge argumentation, sourcing adequacy, or
accuracy — those have poor inter-rater reliability even among trained humans
(Marcoci et al. 2019, ICC 0.29 untrained) and belong to the reviewer, not to a
regex.

Usage:
    python3 lint_oir.py REPORT.md [--json] [--json-out findings.json]
                                  [--no-legal] [--max-sentence 30]

Exit codes:
    0  no HARD findings
    1  one or more HARD findings
    2  usage / file error

Stdlib only. No network.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Lexicons
# ---------------------------------------------------------------------------

# ICD 203 §D.6.e(2)(a) — the two permitted rows of likelihood terms.
ICD203_ROW1 = [
    "almost no chance", "very unlikely", "unlikely", "roughly even chance",
    "very likely", "likely", "almost certainly", "almost certain",
]
ICD203_ROW2 = [
    "highly improbable", "improbably", "improbable",
    "roughly even odds", "highly probable", "probably", "probable",
    "nearly certain",
]
# "remote" is a likelihood term in ICD 203 row 2 and also the commonest
# adjective in incident reporting ("remote access", "remote code execution").
# Only treat it as estimative when it is used as one.
REMOTE_AS_LIKELIHOOD = re.compile(
    r"\b(?:a\s+)?remote\s+(?:chance|possibility|likelihood|probability)\b"
    r"|\bis\s+remote\b|\bare\s+remote\b|\bremains?\s+remote\b", re.I)
ICD203_BANDS = {
    "almost no chance": "01-05%", "remote": "01-05%",
    "very unlikely": "05-20%", "highly improbable": "05-20%",
    "unlikely": "20-45%", "improbable": "20-45%", "improbably": "20-45%",
    "roughly even chance": "45-55%", "roughly even odds": "45-55%",
    "likely": "55-80%", "probable": "55-80%", "probably": "55-80%",
    "very likely": "80-95%", "highly probable": "80-95%",
    "almost certain": "95-99%", "almost certainly": "95-99%",
    "nearly certain": "95-99%",
}

# UK PHIA Probability Yardstick — an equally defensible alternative, with
# deliberate gaps between bands so boundary cases round to a defensible tier.
PHIA_BANDS = {
    "remote chance": "<=5%", "highly unlikely": "10-20%",
    "unlikely": "25-35%", "realistic possibility": "40-49%",
    "likely": "55-75%", "probably": "55-75%",
    "highly likely": "80-90%", "almost certain": ">=95%",
}
PHIA_TERMS = list(PHIA_BANDS)

# Confidence is a claim about the evidence base, not about the world.
CONFIDENCE_TERMS = [
    "high confidence", "moderate confidence", "low confidence",
    "we are confident", "we are highly confident", "high degree of confidence",
    "confidence: high", "confidence: moderate", "confidence: low",
    "with confidence",
]

# Kent (1964) fn.9/10 — stacking hedges multiplies odds into nonsense.
STACKED_HEDGES = [
    r"\bmay\s+well\b", r"\bcould\s+well\b", r"\bmight\s+well\b",
    r"\bcould\s+potentially\b", r"\bmay\s+potentially\b",
    r"\bpossibly\s+may\b", r"\bpossibly\s+could\b", r"\bmight\s+possibly\b",
    r"\bwe\s+believe\s+it\s+is\s+likely\b", r"\bwe\s+think\s+it\s+is\s+likely\b",
    r"\bit\s+is\s+possible\s+that\s+.{0,40}\bmay\b",
    r"\bprobably\s+likely\b", r"\blikely\s+probable\b",
    r"\bseems\s+to\s+possibly\b", r"\bappears\s+to\s+possibly\b",
    r"\bcannot\s+be\s+ruled\s+out\s+that\s+.{0,40}\bmay\b",
]

# CIA DI Style Manual: modifiers that "do little or no work".
# Weakeners drain judgments that have evidence; boosters fake evidence
# that isn't there.
EMPTY_WEAKENERS = ["apparently", "evidently", "seemingly", "purportedly",
                   "ostensibly", "supposedly"]
EMPTY_BOOSTERS = ["obviously", "undoubtedly", "clearly", "of course",
                  "needless to say", "it goes without saying",
                  "without a doubt", "unquestionably"]
# "certainly" is a booster only when it is not part of "almost certainly",
# which is an ICD 203 row-1 term this skill mandates.
BARE_CERTAINLY = re.compile(r"(?<!almost )\bcertainly\b", re.I)

# Kent: unmodified "reportedly" carries no evaluative weight at all.
UNSOURCED_ATTRIBUTION = [
    r"\breportedly\b", r"\bsources\s+indicate\b", r"\bit\s+appears\s+that\b",
    r"\bit\s+is\s+understood\s+that\b", r"\bword\s+is\b",
    r"\bindustry\s+reporting\s+suggests\b", r"\bopen\s+sources\s+say\b",
    r"\bis\s+believed\s+to\s+be\b", r"\bis\s+thought\s+to\s+be\b",
]

# Words that turn a factual record into a legal conclusion or an admission.
# See references/legal-exposure.md for the substitution table and the
# case law behind each one.
LEGAL_EXPOSURE = [
    # "Privacy Breach" / "Proprietary Breach" are NIST SP 800-61r2
    # information-impact category names — quoting a taxonomy is not making a
    # legal conclusion.
    (r"(?<!privacy )(?<!proprietary )(?<!Privacy )(?<!Proprietary )"
     r"\bbreach(?:ed|es)?\b(?!\s*-?\s*(?:notification|notice|response|"
     r"coach|counsel))", "'Breach' is a statutorily defined term whose "
     "definition varies by regulator. Use 'incident', or name the specific "
     "act ('unauthorized access to X'). Reserve 'breach' for counsel."),
    # "failed login/authentication attempt" is standard telemetry vocabulary,
    # not an admission — exclude it so the real cases stay visible.
    (r"(?<!of )\bfail(?:ed|ure|s|ing)\b(?!\s*-?\s*(?:login|logon|log-in|"
     r"attempt|authentication|auth|password|connection|handshake|check|"
     r"closure|over|to\s+start|to\s+resolve|to\s+respond|job|jobs|state|"
     r"node|disk|drive|sensor|probe|health|domain))",
     "Reads as an admission of fault. Describe "
     "what the control did: 'did not execute', 'did not generate an alert', "
     "'was not configured to'."),
    (r"\bnegligen(?:t|ce)\b", "A legal standard of care. Remove; describe the "
     "control state instead."),
    (r"\breckless(?:ly|ness)?\b", "Legal standard of care. Remove."),
    (r"\bcareless(?:ly|ness)?\b", "Legal standard of care. Remove."),
    (r"\bshould\s+have\b", "Counterfactual — reads as an admission. State "
     "what the control did; put the fix in the separate remediation document."),
    (r"\bcould\s+have\s+(?:been\s+)?prevent", "Counterfactual admission. Remove."),
    (r"\bif\s+only\b", "Counterfactual admission. Remove."),
    (r"\bwe\s+knew\b", "Establishes notice — the plaintiff's key element. "
     "State the artifact and date instead: 'Ticket #1234, opened <date>, "
     "referenced CVE-XXXX on Asset Group A'."),
    (r"\bwas\s+known\s+(?:to|since|about)\b", "Establishes notice. Replace "
     "with the artifact and its date."),
    (r"\b(?:inadequate|insufficient|weak|poor|lacking|deficient)\s+"
     r"(?:control|controls|logging|monitoring|security|hygiene|coverage|"
     r"segmentation|visibility|telemetry|oversight)\b",
     "Control *adequacy* is a legal/regulatory conclusion. Describe the "
     "control's configuration and observed behaviour; let the regulator draw "
     "the conclusion."),
    (r"\b(?:control|controls|logging|monitoring|security|hygiene|coverage|"
     r"segmentation|visibility|telemetry|oversight)\s+"
     r"(?:was|were|is|are|had\s+been)\s+"
     r"(?:inadequate|insufficient|weak|poor|lacking|deficient|not\s+"
     r"(?:effective|adequate|sufficient))\b",
     "Control *adequacy* is a legal/regulatory conclusion. Describe the "
     "control's configuration and observed behaviour; let the regulator draw "
     "the conclusion."),
    (r"\broot\s+cause\s+(?:was|is)\s+(?:the\s+)?(?:\w+\s+)?(?:team|analyst|"
     r"engineer|administrator|employee|contractor|vendor)\b",
     "Blame attribution to a person or team, and speculative as to intent. "
     "Use condition-action-evidence: 'The patch management control did not "
     "execute for Asset Group A due to an approval workflow exception'."),
    (r"\bno\s+(?:data|records?|information)\s+(?:was|were)\s+"
     r"(?:exfiltrated|stolen|taken|accessed)\b",
     "Unbounded absolute — one contrary log destroys it. Bound it: 'No "
     "evidence of exfiltration was observed in <log sources> covering "
     "<window>. Retention for <source> begins <date>.'"),
    (r"\bthere\s+(?:was|is)\s+no\s+risk\b", "Unbounded absolute. Bound to "
     "evidence and window."),
    (r"\bimpossible\b(?!\s+travel)", "Unbounded absolute. Bound to evidence "
     "and window."),
    (r"\b(?:we\s+)?(?:responded|acted|contained)\s+immediately\b",
     "Invites contradiction by the timeline. Use absolute UTC timestamps."),
    (r"\bas\s+soon\s+as\s+we\s+(?:learned|knew|found\s+out)\b",
     "Invites contradiction by the timeline. Use absolute UTC timestamps."),
    (r"\bwe\s+recommend\b|\bmust\s+(?:be\s+)?(?:fix|remediat|patch)",
     "Remediation recommendations inside an investigative report were cited "
     "in Wengui v. Clark Hill as proof the document served a business "
     "purpose. Move to a separate remediation plan."),
    (r"\bviolat(?:ed|ion|es)\s+(?:our\s+)?(?:policy|standard|procedure)\b",
     "A self-generated compliance-gap admission. State the facts; leave "
     "policy conformance to a separate, counsel-directed assessment."),
]

# Loose use of "compromised" claims a confirmed CIA loss. Match the verb to
# the evidence.
IMPRECISE_VERBS = [
    (r"(?<!indicators of )(?<!indicator of )(?<!of )\bcompromis(?:ed|e|ing)\b",
     "Claims a confirmed loss of confidentiality/integrity/availability. If "
     "the evidence shows authentication, write 'authenticated to'; if "
     "execution, 'executed on'; if read access, 'accessed'."),
    (r"\bhack(?:ed|er|ing)\b", "Imprecise and colloquial. Name the observed "
     "action or use 'threat actor'."),
    (r"\bmalicious\s+actor\s+successfully\b", "'Successfully' is editorial. "
     "State the observed action."),
]

# Idioms and colloquialisms. These survive spell-check, break machine
# translation, and read as unserious to a regulator.
IDIOMS = [
    r"\bbob'?s\s+your\s+uncle\b", r"\blow[- ]hanging\s+fruit\b",
    r"\bboil\s+the\s+ocean\b", r"\bmove\s+the\s+needle\b",
    r"\bcircle\s+back\b", r"\btouch\s+base\b", r"\bball\s?park\b",
    r"\bat\s+the\s+end\s+of\s+the\s+day\b", r"\bpar\s+for\s+the\s+course\b",
    r"\bsmoking\s+gun\b", r"\bsilver\s+bullet\b", r"\bcan\s+of\s+worms\b",
    r"\bdrop\s+the\s+ball\b", r"\bhit\s+the\s+ground\s+running\b",
    r"\bthrow\s+(?:them|him|her|us)\s+under\s+the\s+bus\b",
    r"\bthe\s+usual\s+suspects\b", r"\bwild\s+goose\s+chase\b",
    r"\bneedle\s+in\s+a\s+haystack\b", r"\brabbit\s+hole\b",
    r"\bgot\s+lucky\b", r"\bdodged\s+a\s+bullet\b",
    r"\bpiece\s+of\s+cake\b", r"\beasy\s+peasy\b", r"\bslam\s+dunk\b",
    r"\bhome\s+run\b", r"\bfull\s+court\s+press\b", r"\bcurve\s?ball\b",
    r"\bno\s+bandwidth\b", r"\bthe\s+usual\s+drill\b",
]

# CIA DI Style Manual "fill-ins" — reserve for when they do work.
FILL_INS = ["basically", "essentially", "in connection with", "in this context",
            "as noted", "at the same time", "indeed", "with reference to",
            "it should be noted that", "it is important to note that",
            "significantly,"]

# Subjective words — the analyst is not deciding whether something is good.
SUBJECTIVE = ["fortunately", "unfortunately", "regrettably", "regretfully",
              "mercifully", "interestingly", "alarmingly", "shockingly",
              "thankfully", "sadly", "amazingly", "surprisingly",
              "concerningly", "worryingly"]

# Verbs that mark a judgment. A judgment needs a likelihood term, a
# confidence statement, or a cited artifact — otherwise it is an unmarked
# opinion.
JUDGMENT_VERBS = [
    r"\bwe\s+assess\b", r"\bwe\s+judge\b", r"\bwe\s+believe\b",
    r"\bwe\s+conclude\b", r"\bwe\s+suspect\b", r"\bit\s+is\s+assessed\b",
    r"\bthe\s+team\s+assesses\b", r"\bassessment\s+is\s+that\b",
    r"\bindicat(?:es|ing)\s+that\b", r"\bsuggests\s+that\b",
    r"\bconsistent\s+with\b", r"\battribut(?:ed|able)\s+to\b",
    r"\bthe\s+(?:most\s+)?likely\s+(?:explanation|vector|cause)\b",
]

# Markers that a sentence is anchored to evidence.
EVIDENCE_MARKERS = [
    r"\[[Ee]\d+\]",                       # [E12] evidence-register reference
    r"\[[Rr]ef[:\s]", r"\bsee\s+Appendix\b", r"\bAppendix\s+[A-Z]\b",
    r"\bEvidence\s+(?:ID|Register|Item)\b",
    r"\bSHA-?256\b", r"\bSHA-?1\b", r"\bMD5\b",
    r"\bper\s+[A-Z][\w.-]+\s+log", r"\blog\s+source\b",
    r"\bquery:", r"\bticket\s*#", r"\bcase\s*#",
]

# --- Structural expectations -------------------------------------------------

REQUIRED_SECTIONS = [
    ("bottom line", r"bottom\s+line|BLUF|executive\s+summary"),
    ("scope and authority", r"scope|purpose\s+and\s+scope|authority"),
    ("timeline", r"timeline|sequence\s+of\s+events|chronology"),
    ("findings", r"findings|observations"),
    ("assessments", r"assessment|analytic\s+judg"),
    ("impact", r"impact|affected|exposure"),
    ("limitations", r"limitation|gaps|what\s+we\s+(?:do\s+not|don'?t)\s+know|"
                    r"collection\s+gaps"),
    ("evidence register", r"evidence\s+register|evidence\s+index|"
                         r"appendix\s*[:\-]?\s*evidence"),
]

# RFC 3339: 2026-07-29T04:13:00Z  /  2026-07-29T04:13:00.123Z  /  ...-07:00
RFC3339 = re.compile(
    r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
    r"(?:Z|[+-]\d{2}:\d{2})"
)
# Anything that smells like a date-time but is not RFC 3339.
LOOSE_TIME = re.compile(
    r"\b(?:"
    r"\d{1,2}/\d{1,2}/\d{2,4}"                       # 07/29/2026
    r"|\d{1,2}:\d{2}\s*(?:[AaPp]\.?[Mm]\.?)"          # 4:13 PM
    r"|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
    r"(?![Z+\-\d:.])"                                # naive, no zone
    r"|\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:EST|EDT|CST|CDT|MST|MDT|PST|PDT|BST|CET|CEST|IST|JST|SGT)\b"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}"
    r")"
)

# Template placeholders. A blank template legitimately contains the shape of
# a judgment without the judgment, and flagging that would make the house
# template fail its own linter.
PLACEHOLDER = re.compile(
    r"\[(?:nn|n{1,3})\s*[-–—]|\[likelihood|\[High\s*\||\[level\]|"
    r"\[section\]|\[quote\]|\[E\]|\[what|\[one\s|\[specific|"
    r"\[systems|\[role\]|…|\[\.\.\.\]|<[a-z][a-z ]+>", re.I)

SEVERITY_WORDS = r"\b(?:critical|high|medium|moderate|low|informational|" \
                 r"emergency|severe|baseline)\b"

CODE_FENCE = re.compile(r"^\s*(```|~~~)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify_lines(text):
    """Tag each line as prose / table / code / heading / quote.

    Only prose lines carry style obligations. IOC tables, log excerpts and
    evidence registers are supposed to look dense and unreadable — running a
    sentence-length check over them produces pure noise.
    """
    out, in_code = [], False
    for i, line in enumerate(text.splitlines(), start=1):
        if CODE_FENCE.match(line):
            in_code = not in_code
            out.append((i, line, "code"))
            continue
        if in_code:
            out.append((i, line, "code"))
        elif line.lstrip().startswith("#"):
            out.append((i, line, "heading"))
        elif line.lstrip().startswith("|") or re.match(r"^\s*\|?[\s:|-]{6,}\|?\s*$", line):
            out.append((i, line, "table"))
        elif line.lstrip().startswith(">"):
            out.append((i, line, "quote"))
        elif re.match(r"^\s{4,}\S", line):
            out.append((i, line, "code"))
        else:
            out.append((i, line, "prose"))
    return out


ABBREV = re.compile(
    r"(?:\b(?:e\.g|i\.e|cf|vs|etc|approx|Inc|Ltd|Corp|Co|No|Nos|Fig|Sec|"
    r"Art|Rev|Dept|Univ|St|Mr|Ms|Dr|Prof|Jr|Sr|v|al|ca|est|min|max|"
    r"[A-Z])\.)$")

# A sentence can start with markup (**Bold:**), a backtick, a digit, a
# bracketed reference, or a lowercase word in a numbered sub-list. Splitting
# only on ". <Capital>" merges a whole four-move assessment block into one
# 45-word "sentence", which then trips the same-sentence confidence rule for
# no reason. That false positive would fire on this skill's own template.
SENT_SPLIT = re.compile(
    r"(?<=[.!?])[ \t]+(?=[\"'(\[`*_#‘“]*[A-Za-z0-9])")


def _split(text):
    parts, buf = [], ""
    for piece in SENT_SPLIT.split(text):
        cand = (buf + " " + piece).strip() if buf else piece
        # Don't split immediately after a known abbreviation or an initial.
        if ABBREV.search(cand.rstrip()):
            buf = cand
            continue
        parts.append(cand)
        buf = ""
    if buf:
        parts.append(buf)
    return [p for p in parts if p.strip()]


def sentences_with_lines(tagged):
    """Yield (sentence, line_no) for prose and quote lines only.

    The line number is tracked per sentence rather than per paragraph, so a
    finding in the fourth sentence of a paragraph anchors to the line it is
    actually on.
    """
    buf = []          # list of (text, lineno)
    for lineno, line, kind in tagged:
        if kind not in ("prose", "quote"):
            if buf:
                yield " ".join(t for t, _ in buf).strip(), buf[0][1]
                buf = []
            continue
        stripped = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line).strip()
        if not stripped:
            if buf:
                yield " ".join(t for t, _ in buf).strip(), buf[0][1]
                buf = []
            continue
        buf.append((stripped, lineno))
        joined = " ".join(t for t, _ in buf)
        parts = _split(joined)
        if len(parts) > 1:
            consumed = 0
            for p in parts[:-1]:
                # Attribute the sentence to the line where it began.
                anchor, run = buf[0][1], 0
                for text, ln in buf:
                    if run + len(text) + 1 > consumed:
                        anchor = ln
                        break
                    run += len(text) + 1
                yield p.strip(), anchor
                consumed += len(p) + 1
            tail = parts[-1]
            buf = [(tail, buf[-1][1])]
    if buf:
        yield " ".join(t for t, _ in buf).strip(), buf[0][1]


def word_count(s):
    return len(re.findall(r"[A-Za-z0-9][\w'/-]*", s))


def has_any(patterns, text, flags=re.I):
    return any(re.search(p, text, flags) for p in patterns)


def find_terms(terms, text):
    """Longest-match-first whole-phrase search. Returns matched terms."""
    hits = []
    for t in sorted(terms, key=len, reverse=True):
        if re.search(r"\b" + re.escape(t) + r"\b", text, re.I):
            if not any(t in h for h in hits):
                hits.append(t)
    return hits


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

class Findings:
    """Collects findings, with a per-check cap.

    An uncapped linter on a long report emits thousands of near-identical
    NOTEs and buries the handful that matter — and if the output is piped
    into a reviewing agent, it buries them in someone's context window too.
    """

    def __init__(self, per_check_cap=25):
        self.items = []
        self.cap = per_check_cap
        self._counts = {}
        self.suppressed = {}

    def add(self, severity, check, line, message, excerpt="", fix=""):
        n = self._counts.get(check, 0) + 1
        self._counts[check] = n
        if self.cap and n > self.cap:
            self.suppressed[check] = self.suppressed.get(check, 0) + 1
            return
        self.items.append({
            "severity": severity,          # HARD | SOFT | NOTE
            "check": check,
            "line": line,
            "message": message,
            "excerpt": excerpt[:220],
            "suggested_fix": fix,
        })

    def counts(self):
        c = {"HARD": 0, "SOFT": 0, "NOTE": 0}
        for i in self.items:
            c[i["severity"]] += 1
        return c


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

BAND_RE = re.compile(
    r"\(?\s*(\d{1,3})\s*[-–—]\s*(\d{1,3})\s*%"
    r"|([<>≤≥])\s*=?\s*(\d{1,3})\s*%")


def parse_band(spec):
    """'55-80%' / '<=5%' / '>=95%' -> (lo, hi)"""
    m = re.match(r"(\d+)-(\d+)%", spec)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"<=?(\d+)%", spec)
    if m:
        return 0, int(m.group(1))
    m = re.match(r">=?(\d+)%", spec)
    if m:
        return int(m.group(1)), 100
    return None


def check_sentences(tagged, f, max_sentence, check_legal, lexicon="icd203"):
    row1_seen, row2_seen = set(), set()
    phia = lexicon == "phia"
    bands = PHIA_BANDS if phia else ICD203_BANDS
    lex_name = "PHIA Probability Yardstick" if phia else "ICD 203"

    for sent, lineno in sentences_with_lines(tagged):
        if not sent or word_count(sent) < 3:
            continue
        low = sent.lower()

        # --- ICD 203 §D.6.e(2)(b): the hard prohibition -------------------
        # "reasonably likely" is a statutory term of art (Reg S-P, SEC Item
        # 1.05), not an estimative judgment. Quoting the standard is correct.
        probe = re.sub(r"reasonably\s+likely", "«statutory»", sent, flags=re.I)
        if phia:
            lk = find_terms(PHIA_TERMS, probe)
        else:
            lk = find_terms(ICD203_ROW1 + ICD203_ROW2, probe)
            if REMOTE_AS_LIKELIHOOD.search(probe):
                lk = lk + ["remote"]
        cf = find_terms(CONFIDENCE_TERMS, sent)
        if lk and cf:
            f.add("HARD", "icd203-mixed-confidence-likelihood", lineno,
                  f"Confidence term ({cf[0]!r}) and likelihood term "
                  f"({lk[0]!r}) in the same sentence. ICD 203 §D.6.e(2)(b) "
                  f"says products 'must not combine a confidence level and a "
                  f"degree of likelihood ... in the same sentence' — they "
                  f"answer different questions and readers merge them.",
                  sent,
                  "Split into two sentences: the judgment with its likelihood "
                  "and inline range, then a separate sentence giving "
                  "confidence and what drives it.")

        # --- Likelihood term with no inline number ------------------------
        if lk:
            if not phia:
                for t in lk:
                    row1_seen.add(t) if t in ICD203_ROW1 else row2_seen.add(t)
            m = BAND_RE.search(sent)
            band = bands.get(lk[0].lower())
            if not m:
                f.add("SOFT", "likelihood-without-inline-range", lineno,
                      f"Likelihood term {lk[0]!r} carries no numeric range in "
                      f"the sentence. Wintle et al. (2019) tested the four ways "
                      f"of presenting a lexicon: readers' best estimate fell "
                      f"inside the intended range 82% of the time with the "
                      f"number inline, against 64-65% with the number in a "
                      f"lookup table or a tooltip and 59% with no guidance. A "
                      f"glossary at the back barely helps; the number has to "
                      f"be in the sentence.",
                      sent,
                      f"Write '{lk[0]} ({band})'." if band else
                      f"Add the numeric range for {lk[0]!r} from the "
                      f"{lex_name} table.")
            elif band:
                # A term with the wrong number is worse than no number: it
                # looks calibrated and is not.
                expected = parse_band(band)
                if m.group(1):
                    got = (int(m.group(1)), int(m.group(2)))
                elif m.group(3) in ("<", "≤"):
                    got = (0, int(m.group(4)))
                else:
                    got = (int(m.group(4)), 100)
                if expected and (abs(got[0] - expected[0]) > 5
                                 or abs(got[1] - expected[1]) > 5):
                    f.add("HARD", "likelihood-band-mismatch", lineno,
                          f"{lk[0]!r} is paired with {got[0]}-{got[1]}%, but "
                          f"the {lex_name} band for that term is {band}. A "
                          f"mismatched pair is worse than no number at all — "
                          f"it reads as calibrated and is not, and the reader "
                          f"has no way to tell which half the analyst meant.",
                          sent,
                          f"Either write '{lk[0]} ({band})' or choose the term "
                          f"whose band contains {got[0]}-{got[1]}%.")

        # --- Stacked hedges ------------------------------------------------
        for pat in STACKED_HEDGES:
            m = re.search(pat, sent, re.I)
            if m:
                f.add("SOFT", "stacked-hedge", lineno,
                      f"Stacked hedge {m.group(0)!r}. Kent (1964, fn. 9): two "
                      f"hedges multiply into odds nobody intended. Kent's "
                      f"example: 'we believe' (75%) doubled with 'likely' "
                      f"(75%) yields odds *worse than* 3 to 2, where the "
                      f"writer meant 3 to 1.",
                      sent, "Keep one likelihood term and delete the rest.")
                break

        # --- Empty modifiers ----------------------------------------------
        for w in EMPTY_WEAKENERS:
            if re.search(r"\b" + w + r"\b", low):
                f.add("SOFT", "empty-weakener", lineno,
                      f"{w!r} weakens a judgment without telling the reader "
                      f"why. CIA DI Style Manual: these modifiers 'do little "
                      f"or no work'.",
                      sent,
                      "Either the evidence supports the claim — then state it "
                      "plainly — or it does not, in which case give a "
                      "likelihood term and range.")
                break
        if BARE_CERTAINLY.search(sent):
            f.add("SOFT", "empty-booster", lineno,
                  "'certainly' tries to strengthen a claim with rhetoric "
                  "instead of evidence.", sent,
                  "Delete, or use 'almost certain (95-99%)' if that is the "
                  "judgment.")
        for w in EMPTY_BOOSTERS:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                f.add("SOFT", "empty-booster", lineno,
                      f"{w!r} tries to strengthen a claim with rhetoric "
                      f"instead of evidence. Also flagged as hyperbole in "
                      f"privilege guidance (MoFo, Shumaker).",
                      sent, "Delete, and cite the artifact instead.")
                break

        # --- Unsourced attribution -----------------------------------------
        for pat in UNSOURCED_ATTRIBUTION:
            m = re.search(pat, sent, re.I)
            if m and not has_any(EVIDENCE_MARKERS, sent):
                f.add("SOFT", "unsourced-attribution", lineno,
                      f"{m.group(0)!r} with no source. Kent: unmodified "
                      f"'reportedly' 'carries no evaluative weight "
                      f"whatsoever'.",
                      sent,
                      "Name the source and characterise it (ICD 206 source "
                      "descriptor), or cut the sentence.")
                break

        # --- Unmarked judgment ----------------------------------------------
        for pat in JUDGMENT_VERBS:
            if re.search(pat, sent, re.I):
                if (not lk and not cf and not has_any(EVIDENCE_MARKERS, sent)
                        and not PLACEHOLDER.search(sent)):
                    f.add("HARD", "unmarked-judgment", lineno,
                          "This sentence makes an analytic judgment but "
                          "carries no likelihood term, no confidence "
                          "statement, and no evidence reference. A reader "
                          "cannot tell whether it is an observation or an "
                          "opinion — and if the report is produced in "
                          "litigation, neither can opposing counsel.",
                          sent,
                          "Either move it to Findings as an observation with "
                          "its evidence ID, or mark it as an assessment with "
                          "a likelihood term + inline range and a separate "
                          "confidence sentence.")
                break

        # --- Legal exposure -------------------------------------------------
        if check_legal:
            for pat, why in LEGAL_EXPOSURE:
                m = re.search(pat, sent, re.I)
                if m:
                    f.add("HARD", "legal-exposure", lineno,
                          f"{m.group(0)!r} — {why}", sent, "")
            for pat, why in IMPRECISE_VERBS:
                m = re.search(pat, sent, re.I)
                if m:
                    f.add("SOFT", "imprecise-verb", lineno,
                          f"{m.group(0)!r} — {why}", sent, "")

        # --- Idioms / colloquialisms ----------------------------------------
        for pat in IDIOMS:
            m = re.search(pat, sent, re.I)
            if m:
                f.add("SOFT", "idiom", lineno,
                      f"{m.group(0)!r} is an idiom. On a distributed team it "
                      f"will not survive translation, and in a produced "
                      f"document it reads as unserious.",
                      sent, "Say the literal thing.")
                break

        # --- Fill-ins / subjective words ------------------------------------
        for w in FILL_INS:
            if re.search(r"\b" + re.escape(w), low):
                f.add("NOTE", "fill-in", lineno,
                      f"{w!r} — CIA DI Style Manual 'fill-in'. Usually "
                      f"deletable with no loss.", sent, "Delete.")
                break
        for w in SUBJECTIVE:
            if re.search(r"\b" + w + r"\b", low):
                f.add("SOFT", "subjective-word", lineno,
                      f"{w!r} editorialises. The report records what happened; "
                      f"it does not decide whether that was good or bad.",
                      sent, "Delete.")
                break

        # --- Mechanics -------------------------------------------------------
        wc = word_count(sent)
        if wc > max_sentence:
            f.add("SOFT", "long-sentence", lineno,
                  f"{wc} words. Long sentences usually carry more than one "
                  f"idea; the Federal Plain Language Guidelines ask for one "
                  f"idea per sentence, and AR 25-50 sets a 15-word average.",
                  sent, "Split at the conjunction.")
        if re.match(r"^\s*(?:There\s+(?:is|are|was|were)|It\s+(?:is|was)\s+"
                    r"(?:noted|determined|observed|found))\b", sent, re.I):
            f.add("NOTE", "weak-opener", lineno,
                  "Opens with an empty subject. AR 25-50 ¶1-39.b(8) tells "
                  "writers to avoid 'It is' / 'There is' openers because they "
                  "bury the actor.",
                  sent, "Start with who did what.")
        # Passive voice is fine when the sentence carries provenance — "was
        # observed in db-audit-01 [E31]" names the source, which is the thing
        # the rule is actually protecting. Only flag provenance-free passives.
        pas = re.search(r"\b(?:was|were|been|being|is|are)\s+"
                        r"(\w+(?:ed|en))\b(?!\s+(?:by\s+)?\w*ing)", sent, re.I)
        if (pas and not re.search(r"\bby\s+[A-Z]", sent)
                and not has_any(EVIDENCE_MARKERS, sent)
                and not RFC3339.search(sent)):
            f.add("NOTE", "agentless-passive", lineno,
                  f"Agentless passive ({pas.group(0)!r}) — the reader cannot "
                  f"tell who or what acted. In an investigation report the "
                  f"actor is usually the finding.",
                  sent, "Name the actor: the adversary, the control, the "
                        "analyst, the system.")

    # Row mixing is a document-level property.
    if not phia and row1_seen and row2_seen:
        f.add("SOFT", "icd203-row-mixing", 0,
              f"Report mixes ICD 203 row 1 terms ({sorted(row1_seen)}) with "
              f"row 2 terms ({sorted(row2_seen)}). ICD 203 permits this only "
              f"with an explicit disclaimer that the two sets mean the same "
              f"thing. Simpler to pick one row and stay in it.",
              "", "Standardise on row 1 for operational reports — it is the "
                  "plainer English and translates better.")


def check_timestamps(tagged, f):
    good = bad = 0
    for lineno, line, kind in tagged:
        if kind == "code":
            continue
        for m in RFC3339.finditer(line):
            good += 1
            if " " in m.group(0):
                f.add("NOTE", "timestamp-space-separator", lineno,
                      "RFC 3339 allows a space in place of 'T' but the strict "
                      "form is safer for downstream parsers.",
                      m.group(0), m.group(0).replace(" ", "T"))
        for m in LOOSE_TIME.finditer(line):
            if RFC3339.search(m.group(0)):
                continue
            bad += 1
            f.add("HARD", "non-rfc3339-timestamp", lineno,
                  f"{m.group(0)!r} is not an unambiguous timestamp. NIST "
                  f"SP 800-92 warns that clock and zone error does not merely "
                  f"blur a timeline, it inverts it — 'timestamps might "
                  f"indicate that event A happened 45 seconds before event B, "
                  f"when event A actually happened two minutes after'. Across "
                  f"regions this is the single most common cause of a "
                  f"correlation that silently reverses causality.",
                  line.strip(),
                  "Normalise to RFC 3339 UTC, e.g. 2026-07-29T04:13:00Z. Keep "
                  "the original local offset in the evidence register — the "
                  "offset itself is analytic signal about the operator.")
    if good == 0 and bad == 0:
        f.add("NOTE", "no-timestamps", 0,
              "No timestamps found. An operational investigation report "
              "without a timeline is a summary, not an investigation.", "", "")
    return good, bad


def check_structure(text, f, tagged=None):
    headings = " \n ".join(l for _, l, k in (tagged or []) if k == "heading")
    # Searching the whole document body would pass any wall of prose that
    # happens to contain the words "timeline" and "findings". Structure is a
    # property of the headings.
    hay = headings if headings.strip() else text
    low = hay.lower()
    for label, pat in REQUIRED_SECTIONS:
        if not re.search(pat, low, re.I):
            sev = "HARD" if label in ("bottom line", "limitations",
                                      "evidence register") else "SOFT"
            f.add(sev, "missing-section", 0,
                  f"No '{label}' section found.",
                  "", f"Add a '{label}' section — see assets/OIR-template.md.")

    # BLUF: the first substantive 150 words should carry the answer.
    body = re.sub(r"^\s*#.*$", "", text, flags=re.M)
    head = " ".join(body.split()[:150])
    if head:
        if not re.search(SEVERITY_WORDS, head, re.I):
            f.add("SOFT", "bluf-missing-severity", 0,
                  "No severity rating in the opening 150 words. Executives, "
                  "audit and counsel read the top and stop; DA PAM 600-67 "
                  "puts the bottom line in the first or second paragraph.",
                  head[:200], "Lead with severity and the one-line answer.")
        if not re.search(r"\b(?:assess|determined|confirmed|no evidence|"
                         r"identified|contained|ongoing|open)\b", head, re.I):
            f.add("SOFT", "bluf-missing-answer", 0,
                  "The opening does not state a conclusion. A reader should "
                  "be able to stop after paragraph one and act correctly.",
                  head[:200], "State what happened, how bad, and what is "
                              "being asked of the reader.")

    # Regulatory-clock language: 'determined' is a term of art. Only fire when
    # the report actually asserts a determination — "no determination has been
    # made" is the correct thing to say and should not be flagged.
    asserts = re.search(
        r"\b(?:we|the\s+\w+|it)\s+(?:have\s+|has\s+|was\s+)?determined\b"
        r"|\bdetermination\s+(?:was|has\s+been)\s+made\b"
        r"|\bit\s+was\s+determined\b", text, re.I)
    denies = re.search(r"\bdetermination\s+has\s+not\b|\bno\s+determination\b"
                       r"|\bnot\s+(?:yet\s+)?been\s+(?:made|determined)\b",
                       text, re.I)
    if asserts and not denies:
        if not re.search(r"\bdetermin\w+\s+(?:at|on)\s+\d{4}-\d{2}-\d{2}", text, re.I):
            f.add("SOFT", "determination-without-timestamp", 0,
                  "The report uses 'determined' but never timestamps the "
                  "determination. In US financial services several clocks "
                  "start at determination, not at discovery — SEC Item 1.05 "
                  "(4 business days), NYDFS §500.17 (72 hours), the banking "
                  "agencies' rule (36 hours). An untimestamped determination "
                  "is a compliance gap.",
                  "", "Write 'Determined at 2026-07-29T04:13:00Z by <role>'.")

    # Privilege / distribution legend.
    if not re.search(r"privileg|attorney[- ]client|work product|"
                     r"distribution|TLP:", text, re.I):
        f.add("NOTE", "no-handling-legend", 0,
              "No handling, distribution or privilege legend. Note that a "
              "legend alone protects nothing — Capital One, Clark Hill and "
              "Rutter's all carried one and all were produced — but its "
              "absence removes even the argument.",
              "", "Add a handling block; write the report assuming it will "
                  "be produced.")


def check_ai_overclaim(tagged, f):
    """Claim-to-source traceability, not stylometry.

    A stylometric AI-detector systematically false-positives on analysts
    writing in a second language, so this does not count em-dashes or look
    for 'delve'. It looks for the failure mode Hagar et al. (2025) actually
    measured in document-grounded LLM output: attribution drift, where an
    attributed opinion becomes a universal statement.
    """
    universalisers = [
        (r"\b(?:all|every|none|no)\s+(?:of\s+the\s+)?(?:host|hosts|system|"
         r"systems|account|accounts|endpoint|endpoints|record|records)\b",
         "Universal quantifier over a population."),
        (r"\bit\s+is\s+(?:well[- ])?(?:known|established|understood)\b",
         "Appeal to general knowledge with no source."),
        (r"\bindustry\s+(?:standard|best\s+practice)\b",
         "Appeal to an unnamed authority."),
        (r"\bthis\s+(?:demonstrates|proves|confirms)\b",
         "Proof claim — very few artifacts prove anything on their own."),
        (r"\btypically|\busually\b|\bgenerally\b.{0,60}\battacker",
         "Generalisation about adversary behaviour presented as observation."),
    ]
    for sent, lineno in sentences_with_lines(tagged):
        for pat, why in universalisers:
            m = re.search(pat, sent, re.I)
            if m and not has_any(EVIDENCE_MARKERS, sent):
                f.add("SOFT", "unsupported-generalisation", lineno,
                      f"{m.group(0)!r} — {why} This is the dominant error mode "
                      f"in AI-assisted drafting: Hagar et al. (2025) found "
                      f"30% of document-grounded LLM responses erred, and the "
                      f"top two error types were editorialising about sources "
                      f"and attribution drift — not invented facts. Fluent, "
                      f"confident, and unsupported.",
                      sent,
                      "Bound it to what was observed, in which sources, over "
                      "which window — or cite the artifact.")
                break


def check_evidence_hygiene(text, f):
    if not re.search(r"\bSHA-?256\b|\bSHA-?1\b|\bMD5\b", text, re.I):
        f.add("NOTE", "no-hashes", 0,
              "No artifact hashes. SWGDE 18-Q-002 §5.3 asks for serial "
              "numbers, hash values or equivalent to uniquely identify each "
              "item; without them a finding is not reproducible.", "", "")
    if not re.search(r"\bretention\b|\baged?\s+out\b|\blog(?:s|ging)?\s+"
                     r"(?:coverage|gap)", text, re.I):
        f.add("SOFT", "no-retention-statement", 0,
              "No statement of log retention or coverage. Every 'no evidence "
              "of X' claim is only as strong as the window it was searched "
              "over; a reader cannot weigh a negative finding without it.",
              "", "State, per source: retention window, coverage gaps, and "
                  "the exact window searched.")
    if not re.search(r"\balternativ\w+\s+(?:hypothes|explanation|considered|"
                     r"account|scenario)|\balternatives\s*:|"
                     r"\bcompeting\s+hypothes|\bruled\s+out\b|"
                     r"\bconsidered\s+and\s+rejected\b|"
                     r"\bthe\s+alternative\b", text, re.I):
        f.add("SOFT", "no-alternatives", 0,
              "No alternative hypotheses are stated or ruled out. ICD 203 "
              "tradecraft standard 4 requires analysis of alternatives, and "
              "NIST SP 800-86 says where there are 'two or more plausible "
              "explanations ... each should be given due consideration'. In "
              "practice this is also the cheapest defence against the "
              "first-hypothesis timeline.",
              "", "Add a short 'Alternatives considered' subsection: what "
                  "else could explain this, and what evidence discriminates.")
    if not re.search(r"\b(?:would|will)\s+change\b|\bindicators?\s+"
                     r"that\s+would|\bwatch\s+items\b|\bif\s+we\s+later\s+"
                     r"(?:observe|find)|\bwould\s+(?:revise|overturn|"
                     r"invalidate)\b", text, re.I):
        f.add("SOFT", "no-change-indicators", 0,
              "No 'what would change this assessment' indicators. ICD 203 "
              "asks for them under three separate standards, and they are "
              "what makes an interim report safe to supersede later — the "
              "alternative is an early conclusion that quietly hardens.",
              "", "Add: 'This assessment would change if <observable>.'")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--json", action="store_true", help="JSON to stdout")
    ap.add_argument("--json-out", help="write JSON findings to this path")
    ap.add_argument("--max-sentence", type=int, default=30)
    ap.add_argument("--no-legal", action="store_true",
                    help="skip the legal-exposure lexicon")
    ap.add_argument("--lexicon", choices=["icd203", "phia"], default="icd203",
                    help="which estimative lexicon the house standard uses")
    ap.add_argument("--severity", choices=["HARD", "SOFT", "NOTE"],
                    default="NOTE",
                    help="minimum severity to report (default NOTE = all)")
    ap.add_argument("--per-check-cap", type=int, default=25,
                    help="max findings per check before summarising the rest; "
                         "0 disables the cap")
    args = ap.parse_args()

    p = Path(args.report)
    if not p.exists():
        print(f"error: {p} not found", file=sys.stderr)
        return 2
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"error: cannot read {p}: {e}", file=sys.stderr)
        return 2
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    tagged = classify_lines(text)

    f = Findings(per_check_cap=args.per_check_cap)
    check_structure(text, f, tagged)
    check_sentences(tagged, f, args.max_sentence, not args.no_legal,
                    args.lexicon)
    good_ts, bad_ts = check_timestamps(tagged, f)
    check_ai_overclaim(tagged, f)
    check_evidence_hygiene(text, f)

    prose = [l for _, l, k in tagged if k == "prose" and l.strip()]
    sents = list(sentences_with_lines(tagged))
    avg = round(sum(word_count(s) for s, _ in sents) / len(sents), 1) if sents else 0

    result = {
        "file": str(p),
        "metrics": {
            "prose_lines": len(prose),
            "sentences": len(sents),
            "avg_sentence_words": avg,
            "rfc3339_timestamps": good_ts,
            "ambiguous_timestamps": bad_ts,
        },
        "lexicon": args.lexicon,
        "counts": f.counts(),
        "suppressed_by_cap": f.suppressed,
        "findings": sorted(f.items,
                           key=lambda x: ({"HARD": 0, "SOFT": 1, "NOTE": 2}[x["severity"]],
                                          x["line"])),
    }

    floor = {"HARD": 0, "SOFT": 1, "NOTE": 2}[args.severity]
    result["findings"] = [
        i for i in result["findings"]
        if {"HARD": 0, "SOFT": 1, "NOTE": 2}[i["severity"]] <= floor]

    if args.json_out:
        try:
            Path(args.json_out).write_text(json.dumps(result, indent=2))
        except OSError as e:
            print(f"error: cannot write {args.json_out}: {e}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        c = result["counts"]
        print(f"\n{p.name} — {c['HARD']} hard, {c['SOFT']} soft, {c['NOTE']} note")
        print(f"  {result['metrics']['sentences']} sentences, "
              f"avg {avg} words; {good_ts} RFC 3339 timestamps, "
              f"{bad_ts} ambiguous\n")
        for item in result["findings"]:
            print(f"[{item['severity']}] line {item['line']} "
                  f"({item['check']})\n    {item['message']}")
            if item["excerpt"]:
                print(f"    > {item['excerpt']}")
            if item["suggested_fix"]:
                print(f"    fix: {item['suggested_fix']}")
            print()
        for check, n in sorted(f.suppressed.items()):
            print(f"[...] {n} further {check!r} finding(s) suppressed by the "
                  f"per-check cap. Raise --per-check-cap to see them all.")
    return 1 if f.counts()["HARD"] else 0


if __name__ == "__main__":
    sys.exit(main())
