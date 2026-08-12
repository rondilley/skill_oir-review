#!/usr/bin/env python3
"""
test_skill.py — regression tests for the oir-review scripts.

Every test here corresponds to a defect that was found and fixed, or to a
safety property the review-token control depends on. Run from the skill
directory:

    python3 scripts/test_skill.py

Stdlib only. Writes to a temp directory and cleans up.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINT = HERE / "lint_oir.py"
PLANT = HERE / "insert_review_tokens.py"
CLEAR = HERE / "clear_review_tokens.py"
ASSETS = HERE.parent / "assets"

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}" + (f" — {detail}" if detail else ""))
        FAILS.append(name)


def lint(tmp, text, *flags):
    p = tmp / "r.md"
    p.write_text(text, encoding="utf-8")
    out = tmp / "r.json"
    subprocess.run([sys.executable, str(LINT), str(p), "--json-out", str(out)]
                   + list(flags), capture_output=True, text=True)
    return json.loads(out.read_text(encoding="utf-8"))


def checks_at(res, minline=1):
    return {f["check"] for f in res["findings"] if f["line"] >= minline}


# ---------------------------------------------------------------------------

def test_linter(tmp):
    print("\nlint_oir.py")

    # The four-move assessment block must split into sentences. Before the
    # fix it collapsed into one 45-word "sentence" and tripped the
    # same-sentence confidence rule on the skill's own template.
    r = lint(tmp, """# Assessments
**A1.** **Judgment:** We assess it is likely (55-80%) that access was via the
VPN [E1]. **Confidence:** Moderate — a single telemetry source. **This would
change if:** logs show earlier access.
""")
    check("four-move block does not trip the same-sentence rule",
          "icd203-mixed-confidence-likelihood" not in checks_at(r))

    # ...but the real violation still fires.
    r = lint(tmp, "We have high confidence that exfiltration is likely.\n")
    check("genuine confidence+likelihood in one sentence still HARD",
          "icd203-mixed-confidence-likelihood" in checks_at(r))

    # Band validation: a term paired with the wrong number is worse than none.
    r = lint(tmp, "We assess it is likely (05-20%) that data left the estate.\n")
    check("wrong band flagged", "likelihood-band-mismatch" in checks_at(r))
    r = lint(tmp, "We assess it is likely (55-80%) that data left the estate.\n")
    check("right band not flagged",
          "likelihood-band-mismatch" not in checks_at(r))

    # PHIA lexicon.
    r = lint(tmp, "It is highly likely (80-90%) that access was via the VPN.\n",
             "--lexicon", "phia")
    check("PHIA correct band clean",
          "likelihood-band-mismatch" not in checks_at(r))
    r = lint(tmp, "It is highly likely (10-20%) that access was via the VPN.\n",
             "--lexicon", "phia")
    check("PHIA wrong band flagged",
          "likelihood-band-mismatch" in checks_at(r))
    r = lint(tmp, "There is a remote chance (<=5%) of undetected persistence.\n",
             "--lexicon", "phia")
    check("PHIA open-ended band parsed",
          "likelihood-without-inline-range" not in checks_at(r))

    # False positives that made the linter net-negative on real reports.
    fps = {
        "impossible travel": "Impossible travel was detected for the account.",
        "failed login": "The gateway recorded 340 failed login attempts.",
        "failed to start": "The nightly backup job failed to start on db-03.",
        "indicators of compromise": "Indicators of compromise are listed below.",
        "remote access": "Remote access via the RDP gateway was observed.",
        "remote code execution": "Remote code execution was achieved there.",
        "almost certainly": "We assess it is almost certainly (95-99%) external.",
        "breach notification": "Breach notification duties sit with counsel.",
        "privacy breach taxonomy": "Information impact: Privacy Breach.",
        "reasonably likely (statutory)":
            "Sensitive customer information was not reasonably likely accessed.",
        "bandwidth": "The link ran at 40% of available bandwidth.",
    }
    for name, line in fps.items():
        r = lint(tmp, line + "\n")
        hits = {f["check"] for f in r["findings"]
                if f["line"] >= 1 and f["severity"] in ("HARD", "SOFT")}
        check(f"no false positive: {name}", not hits, str(hits))

    # True positives must survive the exclusions.
    tps = {
        "breach as conclusion": ("We identified a breach of the VPN.",
                                 "legal-exposure"),
        "control adequacy": ("Logging was insufficient on the file servers.",
                             "legal-exposure"),
        "counterfactual": ("The team should have patched it in March.",
                           "legal-exposure"),
        "unbounded absolute": ("No data was exfiltrated.", "legal-exposure"),
        "recommendation in report": ("We recommend mandatory verification.",
                                     "legal-exposure"),
        "idiom": ("The team had to boil the ocean to find it.", "idiom"),
        "stacked hedge": ("The actor may well have accessed the share.",
                          "stacked-hedge"),
        "empty booster": ("Clearly this was a targeted operation.",
                          "empty-booster"),
        "unsourced attribution": ("Reportedly the vendor has a patch.",
                                  "unsourced-attribution"),
        "unmarked judgment": ("We assess the actor kept access for three days.",
                              "unmarked-judgment"),
    }
    for name, (line, expect) in tps.items():
        r = lint(tmp, line + "\n")
        check(f"still catches: {name}", expect in checks_at(r))

    # Timestamps.
    r = lint(tmp, "The event occurred at 2026-07-16 04:13:00.523Z on the host.\n")
    check("valid RFC 3339 with space and fraction not flagged",
          "non-rfc3339-timestamp" not in checks_at(r))
    r = lint(tmp, "The event occurred at 4:13 PM EDT on 7/14/2026 there.\n")
    check("ambiguous timestamp flagged",
          "non-rfc3339-timestamp" in checks_at(r))

    # Structure is a property of headings, not of the body text.
    r = lint(tmp, "This wall of prose mentions scope, timeline, findings, "
                  "assessment, impact, limitations and the evidence register.\n")
    check("body keywords do not satisfy the structure check",
          any(f["check"] == "missing-section" for f in r["findings"]))

    # Line anchoring is per sentence, not per paragraph.
    r = lint(tmp, "# H\nFirst sentence is fine here today. Second is fine too "
                  "now. Clearly this third one is not fine.\n")
    b = [f for f in r["findings"] if f["check"] == "empty-booster"]
    check("finding anchors to a real line", bool(b) and b[0]["line"] >= 2)

    # Robustness.
    for name, content in [("empty file", ""), ("CRLF", "# H\r\nA line here.\r\n"),
                          ("no headings", "just text\n"),
                          ("only a table", "| a | b |\n|---|---|\n| 1 | 2 |\n")]:
        try:
            lint(tmp, content)
            check(f"handles {name}", True)
        except Exception as e:                       # noqa: BLE001
            check(f"handles {name}", False, str(e))

    # Output cap.
    r = lint(tmp, ("Clearly this is a very obviously long sentence that is "
                   "clearly padded out well beyond thirty words so that it "
                   "reliably trips the long sentence check every single time "
                   "it appears anywhere in this document at all.\n\n") * 60)
    n = sum(1 for f in r["findings"] if f["check"] == "long-sentence")
    check("per-check cap applied", n <= 25 and r["suppressed_by_cap"], str(n))

    # The house template must not fail its own linter.
    out = tmp / "tpl.json"
    subprocess.run([sys.executable, str(LINT), str(ASSETS / "OIR-template.md"),
                    "--json-out", str(out)], capture_output=True, text=True)
    tpl = json.loads(out.read_text(encoding="utf-8"))
    check("house template has zero HARD findings",
          tpl["counts"]["HARD"] == 0, str(tpl["counts"]))


# ---------------------------------------------------------------------------

SAMPLE = """# OIR — INC-1

## 1. Bottom line
Severity High. Access occurred between 2026-07-14T02:11:00Z and 2026-07-17T19:40:00Z.

## 2. Scope and authority
The investigation covered the corporate VPN estate and the engineering file cluster.
Cloud workloads were excluded because they run on separate identity infrastructure.
The engagement was requested by the incident commander and confirmed by the director.

## 4. Findings — observed
The share was read by the account over a sustained period across several working days.

## 7. Limitations and collection gaps
Retention on the gateway is thirty days and older activity cannot be assessed here.

## 9. Narrative
The investigation began after the detection engineering team escalated a rule hit.
The analyst reviewed the surrounding session activity and escalated to the team.
Containment actions were coordinated with the network team the following working day.
Documentation of each step was maintained by the analyst performing the action then.
Communication with stakeholders ran through the established incident channel only.
The engineering organisation provided context on ownership of the directories.

## Annex B — US financial services
The materiality determination remains open and is expected before the week ends.
"""

FORBIDDEN = re.compile(
    r"bottom\s+line|finding|timeline|assess|impact|limitation|evidence|"
    r"annex|appendix|regulat|determin", re.I)
EVIDENTIARY = [r"\d{4}-\d{2}-\d{2}", r"\b[a-f0-9]{32,64}\b",
               r"\b\d{1,3}(?:\.\d{1,3}){3}\b", r"\[[Ee]\d+\]",
               r"\b(?:high|moderate|low)\s+confidence\b",
               r"\b(?:very )?(?:un)?likely\b|\balmost certain"]


def test_tokens(tmp):
    print("\ninsert/clear_review_tokens.py")
    src = tmp / "draft.md"
    src.write_text(SAMPLE, encoding="utf-8")

    def plant(out, manifest, *extra):
        return subprocess.run(
            [sys.executable, str(PLANT), str(src), "--out", str(out),
             "--manifest", str(manifest)] + list(extra),
            capture_output=True, text=True)

    # Refusals.
    r = plant(src, tmp / "m.json")
    check("refuses to overwrite its input", r.returncode == 4)
    r = plant(tmp / "FINAL-report.md", tmp / "m.json")
    check("refuses a final-looking output name", r.returncode == 4)
    r = plant(tmp / "d.UNCLEARED.md", tmp / "m.json", "--seed", "1")
    check("accepts an UNCLEARED output name", r.returncode == 0, r.stderr)
    r2 = subprocess.run(
        [sys.executable, str(PLANT), str(tmp / "d.UNCLEARED.md"),
         "--out", str(tmp / "d2.md"), "--manifest", str(tmp / "m2.json")],
        capture_output=True, text=True)
    check("refuses to double-plant", r2.returncode == 4)
    r = plant(tmp / "d3.md", tmp / "m3.json", "--min", "9", "--max", "2")
    check("rejects min > max", r.returncode == 2)

    # Placement and clearing, across many seeds.
    bad_section = bad_line = bad_evid = bad_clear = 0
    seeds = runs = planted = 0
    for seed in range(40):
        o, m, c = (tmp / f"z{seed}.md", tmp / f"z{seed}.json",
                   tmp / f"c{seed}.md")
        if plant(o, m, "--seed", str(seed), "--density", "60").returncode != 0:
            continue
        runs += 1
        man = json.loads(m.read_text(encoding="utf-8"))
        lines = o.read_text(encoding="utf-8").split("\n")
        planted += len(man["tokens"])
        for t in man["tokens"]:
            if FORBIDDEN.search(t["section"]):
                bad_section += 1
            host = lines[t["line_in_output"] - 1]
            if t["text"] not in host:
                bad_line += 1
                continue
            base = host.replace(" " + t["text"], "")
            if any(re.search(p, base, re.I) for p in EVIDENTIARY):
                bad_evid += 1
        ids = ",".join(f"{t['id']}@{t['line_in_output']}" for t in man["tokens"])
        rc = subprocess.run(
            [sys.executable, str(CLEAR), str(o), "--manifest", str(m),
             "--out", str(c), "--found", ids], capture_output=True, text=True)
        if rc.returncode != 0 or c.read_text(encoding="utf-8") != SAMPLE:
            bad_clear += 1
        seeds += 1

    check(f"tokens never enter a fact-bearing section ({planted} tokens, "
          f"{runs} seeds)", bad_section == 0, f"{bad_section} violations")
    check("manifest line numbers are accurate", bad_line == 0)
    check("tokens never land on evidentiary lines", bad_evid == 0)
    check("clearing restores the source byte-for-byte", bad_clear == 0)

    # The gate: IDs alone must not pass.
    o, m = tmp / "g.UNCLEARED.md", tmp / "g.json"
    plant(o, m, "--seed", "11", "--density", "60")
    man = json.loads(m.read_text(encoding="utf-8"))
    ids_only = ",".join(t["id"] for t in man["tokens"])
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(o), "--manifest", str(m),
         "--out", str(tmp / "g1.md"), "--found", ids_only],
        capture_output=True, text=True)
    check("IDs without line numbers do not pass the gate", rc.returncode == 1,
          rc.stdout[-200:])

    good = ",".join(f"{t['id']}@{t['line_in_output']}" for t in man["tokens"])
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(o), "--manifest", str(m),
         "--out", str(tmp / "g2.md"), "--found", good],
        capture_output=True, text=True)
    check("correct line numbers pass the gate", rc.returncode == 0, rc.stdout)

    wrong = ",".join(f"{t['id']}@{t['line_in_output'] + 40}"
                     for t in man["tokens"])
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(o), "--manifest", str(m),
         "--out", str(tmp / "g3.md"), "--found", wrong],
        capture_output=True, text=True)
    check("wrong line numbers do not pass", rc.returncode == 1)

    # Foreign-token residue scan: a token from another manifest must block.
    contaminated = tmp / "f.UNCLEARED.md"
    contaminated.write_text(
        o.read_text(encoding="utf-8").replace(
            "Communication with stakeholders ran through the established "
            "incident channel only.",
            "Communication with stakeholders ran through the established "
            "incident channel only. Bob's your uncle."),
        encoding="utf-8")
    outp = tmp / "f.CLEARED.md"
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(contaminated), "--manifest", str(m),
         "--out", str(outp), "--found", "none"], capture_output=True, text=True)
    check("foreign token blocks clearing",
          rc.returncode == 3 and not outp.exists(), rc.stderr[:200])

    # Re-wrapped paragraph still clears.
    rewrapped = tmp / "w.UNCLEARED.md"
    t0 = man["tokens"][0]["text"]
    rewrapped.write_text(
        o.read_text(encoding="utf-8").replace(" " + t0, "\n" + t0.replace(" ", "\n", 1)),
        encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(rewrapped), "--manifest", str(m),
         "--out", str(tmp / "w.md"), "--found", "none"],
        capture_output=True, text=True)
    check("re-wrapped paragraph still clears", rc.returncode == 1, rc.stderr[:200])

    # A draft edited past recognition must refuse rather than half-clear.
    broken = tmp / "b.UNCLEARED.md"
    broken.write_text(o.read_text(encoding="utf-8").replace(t0, t0.replace("e", "3")),
                      encoding="utf-8")
    outp = tmp / "b.CLEARED.md"
    rc = subprocess.run(
        [sys.executable, str(CLEAR), str(broken), "--manifest", str(m),
         "--out", str(outp), "--found", "none"], capture_output=True, text=True)
    check("unrecognisable token refuses to write a clean file",
          rc.returncode == 3 and not outp.exists())


def main():
    tmp = Path(tempfile.mkdtemp(prefix="oir-test-"))
    try:
        test_linter(tmp)
        test_tokens(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'FAILED: ' + ', '.join(FAILS) if FAILS else 'All tests passed.'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
