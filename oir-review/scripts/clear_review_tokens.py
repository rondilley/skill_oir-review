#!/usr/bin/env python3
"""
clear_review_tokens.py — verify the read happened, then remove the tokens.

This is the gate, and it is a gate only because it demands proof of location.
Naming token IDs proves nothing: the IDs are sequential and guessable. The
reviewer must supply the line number where each token was found, and those
line numbers are checked against the manifest. That is the difference between
a checkable claim and a self-report.

The script always removes every token — leaving one behind would be worse
than never planting them — but it records what the reviewer found unaided,
and it refuses to write a clean file if:

  * any manifest token cannot be located (the draft was edited beyond
    recognition, or the wrong manifest was supplied), or
  * ANY string from the full token bank survives in the output, including
    tokens from some earlier manifest this run knows nothing about. That
    second scan is what closes the re-planting path: a token planted in an
    earlier round cannot ride through a later clearing unseen.

Usage:
    python3 clear_review_tokens.py DRAFT.UNCLEARED.md \\
        --manifest tokens.json --out DRAFT.CLEARED.md \\
        --found RT-01@37,RT-03@112 --reviewer "A. Analyst" \\
        --cleared-at 2026-07-29T18:00:00Z [--log clearing.jsonl]

    # reviewer located nothing:
    ... --found none

`--found` accepts `ID@line`. A line within +/- --line-tolerance (default 3)
of the manifest counts as located, which absorbs ordinary editing. `ID` with
no line is recorded as *claimed but unproven* and does not count.

Exit codes:
    0  cleared, every token proven located
    1  cleared, one or more tokens missed or unproven — re-read warranted
    2  usage / file error
    3  residue detected or a token could not be located — no clean file written

Stdlib only. No network.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from insert_review_tokens import ALL_TOKEN_TEXTS
except Exception:                                    # pragma: no cover
    ALL_TOKEN_TEXTS = set()

BANNER_RE = re.compile(r"^> \*\*DRAFT — UNCLEARED.*?(?=\n(?!>))", re.S | re.M)


def parse_found(spec):
    """'RT-01@37,RT-03' -> {'RT-01': 37, 'RT-03': None}"""
    out = {}
    if spec.strip().lower() in ("", "none"):
        return out
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "@" in chunk:
            tid, _, ln = chunk.partition("@")
            try:
                out[tid.strip().upper()] = int(ln.strip())
            except ValueError:
                out[tid.strip().upper()] = None
        else:
            out[chunk.upper()] = None
    return out


def normalise(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tokened_draft")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--found", default="",
                    help="comma-separated ID@line pairs, or 'none'")
    ap.add_argument("--reviewer", default="(unrecorded)")
    ap.add_argument("--cleared-at", default="",
                    help="RFC 3339 UTC timestamp of the clearing")
    ap.add_argument("--line-tolerance", type=int, default=3)
    ap.add_argument("--log", help="append a clearing record to this JSONL file")
    args = ap.parse_args()

    draft_p, man_p = Path(args.tokened_draft), Path(args.manifest)
    for p in (draft_p, man_p):
        if not p.exists():
            print(f"error: {p} not found", file=sys.stderr)
            return 2
    try:
        manifest = json.loads(man_p.read_text())
        tokens = manifest["tokens"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"error: {man_p} is not a usable token manifest ({e})",
              file=sys.stderr)
        return 2

    text = draft_p.read_text(encoding="utf-8", errors="replace")
    found = parse_found(args.found)
    ids = {t["id"] for t in tokens}
    ghosts = sorted(set(found) - ids)

    # --- Verify location claims -------------------------------------------
    proven, unproven, missed = [], [], []
    for t in tokens:
        if t["id"] not in found:
            missed.append(t)
        elif found[t["id"]] is None:
            unproven.append(t)
        else:
            claimed = found[t["id"]]
            actual = t.get("line_in_output")
            if actual is None or abs(claimed - actual) <= args.line_tolerance:
                proven.append(t)
            else:
                unproven.append(dict(t, claimed_line=claimed))

    # --- Remove, tolerating re-wrapped paragraphs --------------------------
    unmatched = []
    for t in tokens:
        for needle in (" " + t["text"], t["text"]):
            if needle in text:
                text = text.replace(needle, "", 1)
                break
        else:
            # The paragraph may have been re-wrapped; match on collapsed
            # whitespace so ordinary editing does not strand a token.
            pat = re.compile(r"\s*" + r"\s+".join(
                re.escape(w) for w in t["text"].split()))
            m = pat.search(text)
            if m:
                text = text[:m.start()] + text[m.end():]
            else:
                unmatched.append(t["id"])

    text = BANNER_RE.sub("", text).lstrip("\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip("\n") + "\n"

    # --- Residue: this manifest, then the WHOLE bank -----------------------
    flat = normalise(text)
    residue = [t["id"] for t in tokens if normalise(t["text"]) in flat]
    foreign = sorted(s for s in ALL_TOKEN_TEXTS
                     if normalise(s) in flat
                     and s not in {t["text"] for t in tokens})

    if unmatched or residue or foreign:
        print("REFUSING TO WRITE A CLEAN FILE.", file=sys.stderr)
        if unmatched:
            print(f"  Not found in the draft: {unmatched}. Either the draft "
                  f"was rewritten past recognition or the wrong manifest was "
                  f"supplied. Re-plant on the current draft; do not hand-remove.",
                  file=sys.stderr)
        if residue:
            print(f"  Still present after removal: {residue}", file=sys.stderr)
        if foreign:
            print(f"  Tokens from a DIFFERENT manifest are present in this "
                  f"draft — this file was tokened more than once, and clearing "
                  f"it with only this manifest would leave those behind:",
                  file=sys.stderr)
            for s in foreign:
                print(f"    \"{s}\"", file=sys.stderr)
            print("  Locate the earlier manifest and clear with that first.",
                  file=sys.stderr)
        return 3

    Path(args.out).write_text(text, encoding="utf-8", newline="\n")

    record = {
        "schema": "oir-review-clearing/2",
        "source_manifest": str(man_p),
        "cleared_file": args.out,
        "cleared_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "reviewer": args.reviewer,
        "cleared_at": args.cleared_at or "(not supplied)",
        "tokens_planted": len(tokens),
        "tokens_proven_located": len(proven),
        "tokens_claimed_unproven": [t["id"] for t in unproven],
        "tokens_missed": [
            {"id": t["id"], "class": t["class"], "class_name": t["class_name"],
             "section": t["section"], "text": t["text"]} for t in missed],
        "unknown_ids_supplied": ghosts,
    }
    if args.log:
        with open(args.log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    print(f"Cleared {len(tokens)} review tokens -> {args.out}")
    print(f"Reviewer: {args.reviewer}")
    print(f"Proven located: {len(proven)}/{len(tokens)}")
    if ghosts:
        print(f"IDs supplied that are not in the manifest: {ghosts}")
    if unproven:
        print(f"\nClaimed without a matching line number: "
              f"{[t['id'] for t in unproven]}")
        print("  These do not count. The line number is the proof; an ID on "
              "its own is a guess, and the IDs are sequential.")
    if missed or unproven:
        shown = missed + [t for t in unproven]
        print("\nNot located — these are the parts that did not get a careful "
              "read:\n")
        by_section = {}
        for t in shown:
            by_section.setdefault(t["section"], []).append(t)
        for section, ts in by_section.items():
            print(f"  §{section}")
            for t in ts:
                print(f"    {t['id']} [{t['class_name']}]  \"{t['text']}\"")
        print("\nWhere they were missed matters more than how many. A cluster "
              "in one section means that section was skimmed — go back to it "
              "before signing off. Class C misses (nonexistent citations) mean "
              "citations were not checked, which is the most consequential "
              "kind of miss in a report that may be produced in litigation.")
        print("\nNote also that tokens are never planted in the findings, "
              "timeline, assessments, impact, limitations, evidence register "
              "or annexes. Nothing in those sections was verified by this "
              "control; they need a deliberate read of their own.")
        return 1

    print("\nEvery token was located with a matching line number. The read is "
          "verified for the narrative sections. The fact-bearing sections "
          "carry no tokens and still need a deliberate read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
