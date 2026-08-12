#!/usr/bin/env python3
"""
insert_review_tokens.py — plant expert-detectable markers in a review draft
so that a human has to actually read it before it ships.

WHY THIS EXISTS
---------------
An AI-edited report reads well. That is exactly the problem: fluency is what
reviewers use as their proxy for correctness, so a clean draft gets skimmed
and approved. Review tokens break the proxy. Each token is a short clause
that a competent security analyst spots instantly on a careful read and that
a spell-checker, a grammar tool, or a model skimming for style glides past.
The draft cannot be cleared until the reviewer reports each token *and the
line it is on* — so "I read it" becomes a checkable claim.

This is a deliberate-error control, the same idea as proof marks in
typesetting or seeded defects in software inspection.

SAFETY RAILS (enforced in code, not by convention)
--------------------------------------------------
1. Tokens are only ever ADDED as a self-contained clause. No existing word,
   number, name, timestamp, hash or citation is ever altered.
2. Tokens never enter a fact-bearing section. The allowlist below is
   deliberately narrow: scope, background, narrative, methodology, approach,
   next steps. Findings, timeline, assessments, impact, limitations, the
   bottom line, the evidence register and every annex are off limits, because
   a token there would corrupt the meaning of a finding even though it alters
   no character of it.
3. Tokens never land on a line carrying a timestamp, hash, IP, CVE, CIDR,
   account, evidence reference, record count, money figure, or any
   likelihood/confidence marker.
4. The script REFUSES to run on a file that already carries the banner. This
   closes the re-planting path, which is otherwise how a token from an
   earlier manifest survives into a file named CLEARED.
5. The script refuses to overwrite its input, and refuses output filenames
   that look final or external.
6. Every token is recorded verbatim with its line, so clearing is exact and
   the clearing step can scan for the *entire* token bank, not just this
   manifest.

Never run this on a final, external, or regulator-facing version.

Usage:
    python3 insert_review_tokens.py DRAFT.md \\
        --out DRAFT.UNCLEARED.md --manifest tokens.json [--density 400]
        [--min 3] [--max 12] [--seed 1234] [--allow-section REGEX]

Exit codes: 0 planted · 2 usage/file error · 3 no safe insertion point
            · 4 refused (already tokened, or unsafe output path)

Stdlib only. No network.
"""

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Token bank
# ---------------------------------------------------------------------------
# Three classes, each failing a different reader.
#
#   A — domain-semantic anomaly. Technically shaped, internally impossible.
#       An analyst blinks; a fluency-oriented model sees well-formed jargon.
#   B — register breach. An idiom in formal prose. Obvious to any careful
#       reader, and it doubles as practice for the idiom problem on a
#       distributed team.
#   C — plausible-but-nonexistent citation. Trains the sourcing reflex: a
#       reviewer who checks citations finds it at once, and a reviewer who
#       trusts citations is exactly who this control is aimed at.
#
# Every entry is a complete, deletable clause about *process*, never about
# what the adversary did or what an artifact showed — combined with the
# section allowlist, that keeps a token from ever contradicting a finding.

TOKEN_BANK = [
    # --- Class A: domain-semantic anomalies --------------------------------
    ("A", "Case notes were timestamped against the switch's spanning-tree priority."),
    ("A", "Analyst workstations were segmented by lowering their DNS TTL to zero."),
    ("A", "The case file was checksummed using the BGP community string."),
    ("A", "Working copies were stored on a share mounted over ICMP."),
    ("A", "Access to the case channel was enforced at Layer 1."),
    ("A", "Reviewer assignments were tracked in the DHCP scope."),
    ("A", "Draft versions were reconciled by inspecting the NTP stratum."),
    ("A", "The investigation timeline was rendered from the SNMP read-only community."),
    ("A", "Handover notes were signed with the load balancer's TLS session ticket."),
    ("A", "The case record was archived by clearing the browser cache on the server."),
    ("A", "Reviewer permissions were revoked at the certificate authority."),
    ("A", "Task priority within the workstream was set by decrementing the process nice value."),
    ("A", "Notes were replicated to the team wiki through the SPAN port's ARP table."),
    ("A", "Shift handover was scheduled against the appliance's MTU."),
    ("A", "The evidence index was sorted by SPF alignment."),
    # --- Class B: register breaches ----------------------------------------
    ("B", "Bob's your uncle."),
    ("B", "Long story short, we got lucky here."),
    ("B", "Frankly, this one nearly slipped through the net."),
    ("B", "That part was, to be fair, a bit of a wild goose chase."),
    ("B", "The team burned the midnight oil on this one."),
    ("B", "In short, we dodged a bullet."),
    ("B", "It was, as they say, a needle in a haystack."),
    ("B", "Easy peasy from there."),
    ("B", "Anyway, moving swiftly along."),
    ("B", "This is where things got properly interesting."),
    # --- Class C: nonexistent citations ------------------------------------
    ("C", "This step follows NIST SP 800-61r4 §4.2."),
    ("C", "Handling was consistent with ISO/IEC 27099:2023 Annex D."),
    ("C", "The workflow follows CVSS v4.2 environmental scoring guidance."),
    ("C", "The taxonomy used here is defined in ICD 214 §D.3."),
    ("C", "Retention followed FFIEC IT Handbook Appendix K."),
    ("C", "Case severity was mapped using the NCISS v3 numeric bands."),
    ("C", "Evidence handling followed RFC 9911 §5."),
    ("C", "Workstream naming aligns with MITRE ATT&CK tactic TA0102."),
    ("C", "Case notes are recorded per ISO 8601-4:2024 §7.1."),
    ("C", "Terminology is drawn from the FIRST CTI-SIG WEP annex, revision 5."),
]

ALL_TOKEN_TEXTS = {t for _, t in TOKEN_BANK}

# ---------------------------------------------------------------------------
# Section policy — allowlist, not blocklist
# ---------------------------------------------------------------------------
# A blocklist fails open: any heading nobody thought of becomes a target.
# Everything not named here is protected.

ALLOWED_SECTIONS = re.compile(
    r"scope|authority|background|narrative|methodolog|approach|"
    r"how\s+(?:this|the)\s+investigation|process|next\s+steps|"
    r"investigation\s+summary|overview\s+of\s+(?:work|activity)|"
    r"context|introduction",
    re.I)

# Belt and braces: even inside an allowed heading, these words in the heading
# path veto insertion.
VETO_IN_PATH = re.compile(
    r"bottom\s+line|BLUF|executive|finding|observ|timeline|chronolog|"
    r"assess|judg|impact|affected|exposure|limitation|gap|evidence|"
    r"custody|register|index|annex|appendix|regulat|notification|legal|"
    r"privileg|determin|conclusion|recommend|remediat",
    re.I)

# ---------------------------------------------------------------------------
# Line-level exclusions
# ---------------------------------------------------------------------------

EVIDENTIARY = [
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}",
    r"\b[a-fA-F0-9]{32,64}\b",
    r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
    r"\b(?:[0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{0,4}\b",
    r"\bCVE-\d{4}-\d{4,}\b",
    r"/\d{1,2}\b",
    r"\[[Ee]\d+\]",
    r"\bSHA-?(?:1|256)\b|\bMD5\b",
    r"\b[A-Z]{2,}\\[A-Za-z0-9._-]+\b",
    r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    r"[$£€]\s?[\d,]+",
    r"\b\d{1,3}(?:,\d{3})+\b",
    r"\b\d+\s*(?:records?|accounts?|hosts?|systems?|users?|customers?|files?)\b",
    r"\bticket\s*#|\bcase\s*#|\bINC\d+",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

JUDGMENT_MARKERS = [
    r"\b(?:almost no chance|very unlikely|unlikely|roughly even (?:chance|odds)|"
    r"very likely|likely|almost certain(?:ly)?|highly improbable|"
    r"improbabl[ey]|highly probable|probabl[ey]|nearly certain|"
    r"realistic possibility|highly likely|highly unlikely|remote chance)\b",
    r"\bconfidence\b",
    r"\bwe\s+(?:assess|judge|believe|determine|conclude|suspect)\w*\b",
    r"\b(?:assessed|determined|judged|concluded)\b",
    r"\b\d{1,3}\s*[-–—]\s*\d{1,3}\s*%",
]

# Word-boundary matching matters here: "UNCLEARED" contains "cleared", and
# refusing to write the file this script is supposed to produce would be a
# fine joke and a useless control.
UNSAFE_OUT = re.compile(
    r"\bfinal\b|\bregulat\w*|\bexternal\b|\bsubmit\w*|\bfiled\b|"
    r"\b8-?k\b|\bnotification\b|\bcounsel\b|\bboard\b|"
    r"(?<!un)\bcleared\b|\bissued\b|\breleased?\b|\bapproved\b",
    re.I)

CODE_FENCE = re.compile(r"^\s*(```|~~~)")
BANNER_SENTINEL = "DRAFT — UNCLEARED. NOT FOR DISTRIBUTION."

BANNER = (
    "> **DRAFT — UNCLEARED. NOT FOR DISTRIBUTION.**\n"
    "> This draft contains {n} review tokens: short inserted clauses that are\n"
    "> wrong in a way a security analyst will notice and a spell-checker will\n"
    "> not. Read the whole document, note each token *and its line number*,\n"
    "> then run `clear_review_tokens.py`. Clearing requires the line numbers —\n"
    "> naming the IDs alone will not pass. Until the file has been cleared, it\n"
    "> is not a report and must not be distributed.\n"
)


def heading_path(stack):
    return " / ".join(h for h in stack if h)


def section_allowed(stack):
    path = heading_path(stack)
    if not path:
        return False           # preamble is fact-bearing; fail closed
    if VETO_IN_PATH.search(path):
        return False
    return bool(ALLOWED_SECTIONS.search(path))


def is_insertable(line, kind, stack, extra_allow):
    if kind != "prose":
        return False
    s = line.strip()
    if len(s.split()) < 12:
        return False
    if not s.endswith((".", ".\"", ".'", ".)")):
        return False
    if s.startswith(("-", "*", "+", ">", "|")) or re.match(r"^\d+[.)]\s", s):
        return False
    if not (section_allowed(stack)
            or (extra_allow and extra_allow.search(heading_path(stack))
                and not VETO_IN_PATH.search(heading_path(stack)))):
        return False
    for pat in EVIDENTIARY + JUDGMENT_MARKERS:
        if re.search(pat, line, re.I):
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--density", type=int, default=400,
                    help="approx. one token per N eligible words (default 400)")
    ap.add_argument("--min", type=int, default=3, dest="min_tokens")
    ap.add_argument("--max", type=int, default=12, dest="max_tokens")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--allow-section", default=None,
                    help="regex for additional heading names that may receive "
                         "tokens; the fact-bearing veto still applies")
    ap.add_argument("--force-unsafe-out", action="store_true",
                    help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.min_tokens > args.max_tokens:
        print(f"error: --min ({args.min_tokens}) exceeds --max "
              f"({args.max_tokens})", file=sys.stderr)
        return 2

    src, out_path = Path(args.draft), Path(args.out)
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 2
    if out_path.resolve() == src.resolve():
        print("error: --out must not be the input file. Overwriting the clean "
              "draft leaves no un-tokened source to re-plant from.",
              file=sys.stderr)
        return 4
    if UNSAFE_OUT.search(out_path.name) and not args.force_unsafe_out:
        print(f"error: refusing to write to {out_path.name!r} — the filename "
              f"suggests a final, external or already-cleared artifact. Review "
              f"tokens belong only on an internal review draft.",
              file=sys.stderr)
        return 4

    raw = src.read_text(encoding="utf-8", errors="replace")
    if BANNER_SENTINEL in raw or any(t in raw for t in ALL_TOKEN_TEXTS):
        print("error: this file already contains review tokens or the "
              "UNCLEARED banner. Planting a second set is how a token from an "
              "earlier manifest survives into a file marked CLEARED — the "
              "second clearing only knows about the second manifest. Clear the "
              "existing tokens first, then re-plant on the cleared draft.",
              file=sys.stderr)
        return 4

    rng = random.Random(args.seed)
    extra_allow = re.compile(args.allow_section, re.I) if args.allow_section else None
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    # Tag lines, tracking the full heading stack so a sub-heading cannot
    # silently unprotect the section it sits inside.
    tagged, in_code, stack = [], False, [""] * 7
    for line in lines:
        if CODE_FENCE.match(line):
            in_code = not in_code
            tagged.append((line, "code", tuple(stack)))
            continue
        if in_code:
            kind = "code"
        elif line.lstrip().startswith("#"):
            m = re.match(r"^\s*(#+)\s*(.*)$", line)
            lvl = min(len(m.group(1)), 6)
            stack[lvl] = m.group(2)
            for deeper in range(lvl + 1, 7):
                stack[deeper] = ""
            kind = "heading"
        elif line.lstrip().startswith("|"):
            kind = "table"
        elif line.lstrip().startswith(">"):
            kind = "quote"
        elif re.match(r"^\s{4,}\S", line):
            kind = "code"
        else:
            kind = "prose"
        tagged.append((line, kind, tuple(stack)))

    candidates = [i for i, (l, k, st) in enumerate(tagged)
                  if is_insertable(l, k, st, extra_allow)]
    eligible_words = sum(
        len(l.split()) for l, k, st in tagged
        if k == "prose" and (section_allowed(st)
                             or (extra_allow
                                 and extra_allow.search(heading_path(st))
                                 and not VETO_IN_PATH.search(heading_path(st)))))

    n = max(args.min_tokens,
            min(args.max_tokens, eligible_words // max(1, args.density)))

    if not candidates:
        print("error: no safe insertion point. Every prose paragraph is either "
              "in a fact-bearing section (findings, timeline, assessments, "
              "impact, limitations, evidence, annexes) or carries evidentiary "
              "content. Tokens never enter those, so none were planted — that "
              "is the correct outcome, not a failure. Review this draft by "
              "hand, or use --allow-section to name a narrative heading that "
              "is safe to mark.", file=sys.stderr)
        return 3

    if len(candidates) < n:
        print(f"note: only {len(candidates)} safe insertion point(s) available "
              f"(wanted {n}). Fewer tokens means weaker verification, and "
              f"nothing in the fact-bearing sections is being checked at all — "
              f"read those by hand.", file=sys.stderr)
    n = min(n, len(candidates))

    # Spread across the document so a reviewer cannot find them all early and
    # stop reading.
    ordered = sorted(candidates)
    if n == 1:
        chosen = [rng.choice(ordered)]
    else:
        size = max(1, len(ordered) // n)
        picks = []
        for b in range(n):
            seg = ordered[b * size:(b + 1) * size] or ordered
            seg = [s for s in seg if s not in picks] or \
                  [s for s in ordered if s not in picks]
            if seg:
                picks.append(rng.choice(seg))
        chosen = sorted(set(picks))

    by_class = {"A": [], "B": [], "C": []}
    for cls, txt in TOKEN_BANK:
        by_class[cls].append(txt)
    for v in by_class.values():
        rng.shuffle(v)
    order = (["A", "B", "C"] * ((len(chosen) // 3) + 2))[:len(chosen)]
    rng.shuffle(order)

    manifest_tokens = []
    banner_lines = BANNER.count("\n") + 1      # banner + blank line
    for idx, line_i in enumerate(chosen):
        cls = order[idx]
        if not by_class[cls]:
            cls = next((c for c in "ABC" if by_class[c]), None)
            if cls is None:
                break
        token_text = by_class[cls].pop()
        line, kind, st = tagged[line_i]
        tagged[line_i] = (line.rstrip() + " " + token_text, kind, st)
        manifest_tokens.append({
            "id": f"RT-{idx + 1:02d}",
            "class": cls,
            "class_name": {"A": "domain-semantic anomaly",
                           "B": "register breach",
                           "C": "nonexistent citation"}[cls],
            "text": token_text,
            "line_in_output": line_i + 1 + banner_lines,
            "section": heading_path(st) or "(preamble)",
        })

    body = "\n".join(l for l, _, _ in tagged).rstrip("\n")
    out_text = BANNER.format(n=len(manifest_tokens)) + "\n" + body + "\n"
    out_path.write_text(out_text, encoding="utf-8", newline="\n")

    # Confirm the recorded line numbers are right — a wrong answer key would
    # make honest reviewers fail the gate.
    written = out_text.split("\n")
    for t in manifest_tokens:
        assert t["text"] in written[t["line_in_output"] - 1], \
            f"internal error: {t['id']} line index wrong"

    manifest = {
        "schema": "oir-review-tokens/2",
        "source_draft": str(src),
        "tokened_draft": str(out_path),
        "tokened_sha256": hashlib.sha256(out_text.encode()).hexdigest(),
        "token_count": len(manifest_tokens),
        "seed": args.seed,
        "tokens": manifest_tokens,
        "instructions": (
            "This file is the answer key. Do not give it to the reviewer. The "
            "reviewer reads the draft and reports each token they find with "
            "its line number; clearing verifies the line numbers against this "
            "manifest, which is what makes the read checkable rather than "
            "self-reported."
        ),
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2))

    print(f"Planted {len(manifest_tokens)} review tokens in {out_path}")
    print(f"Manifest (ANSWER KEY — hold it back from the reviewer): "
          f"{args.manifest}")
    for t in manifest_tokens:
        print(f"  {t['id']}  class {t['class']}  line {t['line_in_output']}  "
              f"§{t['section'][:44]}")
    print("Class counts: " + ", ".join(
        f"{c}={sum(1 for t in manifest_tokens if t['class'] == c)}"
        for c in "ABC"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
