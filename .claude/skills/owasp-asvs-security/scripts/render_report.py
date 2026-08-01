#!/usr/bin/env python3
"""
Render audit reports from a run's findings.json.

Writes to  asvs-audit/reports/<run-date>/ :
  V1.md ... V14.md   - one per chapter touched (findings first, passes collapsed)
  rollup.html        - 14-chapter scorecard (mirrors the workbook Dashboard)

Usage:  python3 scripts/render_report.py <run-date>
Run from the repo root. Reads the pinned requirement catalog from the skill's
data/ dir (for section names and descriptions); the run's verdicts come from
asvs-audit/state/<run-date>/findings.json.
"""
import json
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(HERE, "data", "asvs-4.0.3-l2.json")

SEV_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, None: 4}
# Actionable findings only. NEEDS_REVIEW / CARRY_FORWARD / needs_human land in
# the review bucket instead — see bucketize() — so nothing is counted twice.
FINDING_STATUSES = {"FAIL", "REGRESSION"}
CHAPTER_NAMES = {}  # filled from the catalog


def load():
    with open(CATALOG, encoding="utf-8") as f:
        doc = json.load(f)
    for r in doc["requirements"]:
        CHAPTER_NAMES[r["chapter"]] = r["chapter_name"]
    return doc


def bucketize(results):
    """Partition a chapter's results into mutually exclusive buckets so the
    chapter report and the rollup scorecard always agree and never double-count.
    An item lands in exactly one of: findings (act now), review (human needed),
    passes (clean). Findings are severity-sorted; the caller sorts passes."""
    findings, review, passes = [], [], []
    for r in results:
        if r["status"] in FINDING_STATUSES:
            findings.append(r)
        elif r["status"] in ("NEEDS_REVIEW", "CARRY_FORWARD") or r.get("needs_human"):
            review.append(r)
        elif r["status"] in ("PASS", "RESOLVED_CONFIRMED"):
            passes.append(r)
        else:  # unknown/unexpected status — surface it rather than hide it
            review.append(r)
    findings.sort(key=lambda r: SEV_ORDER.get(r.get("severity"), 4))
    return findings, review, passes


def chapter_report(ch, ch_name, results, baseline_by_id):
    n = len(results)
    status_counts = {}
    for r in results:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    findings, review, passes = bucketize(results)

    L = [f"# {ch} — {ch_name}", ""]
    L.append(f"**Assessed:** {n}  |  "
             f"**Findings:** {len(findings)}  |  "
             f"**Needs human review:** {len(review)}  |  "
             f"**Pass/Resolved:** {len(passes)}")
    L.append("")
    L.append("Status breakdown: " +
             ", ".join(f"{k} {v}" for k, v in sorted(status_counts.items())))
    L.append("")

    if findings:
        L += ["## Findings (act on these)", ""]
        for r in findings:
            b = baseline_by_id.get(r["req_id"], {})
            L.append(f"### {r['req_id']} — {r.get('severity','?')} — {r['status']}")
            L.append(f"*{b.get('section')} {b.get('section_name','')}*")
            L.append("")
            L.append(f"> {b.get('description','')}")
            L.append("")
            L.append(f"- **Evidence:** {r.get('evidence','—')}")
            L.append(f"- **Remediation:** {r.get('remediation','—')}")
            if r.get("owner"):
                L.append(f"- **Owner:** {r['owner']}")
            L.append(f"- **Tier:** {r.get('tier','—')}")
            L.append("")

    if review:
        L += ["## Needs human review (carry-forward / not code-verifiable)", ""]
        for r in review:
            b = baseline_by_id.get(r["req_id"], {})
            L.append(f"- **{r['req_id']}** ({b.get('section_name','')}): "
                     f"{r.get('evidence') or r.get('remediation') or 'confirm with team'}")
        L.append("")

    L += ["<details><summary>Passing / resolved "
          f"({len(passes)})</summary>", ""]
    for r in sorted(passes, key=lambda r: r["req_id"]):
        L.append(f"- {r['req_id']} — {r['status']}")
    L += ["", "</details>", ""]
    return "\n".join(L)


def rollup_html(by_chapter, run_date, scope):
    rows = []
    tot = {"findings": 0, "review": 0, "pass": 0, "assessed": 0}
    for ch in sorted(by_chapter, key=lambda c: int(c[1:])):
        rs = by_chapter[ch]
        findings, review, passes = bucketize(rs)
        f, rev, p = len(findings), len(review), len(passes)
        tot["findings"] += f; tot["review"] += rev; tot["pass"] += p
        tot["assessed"] += len(rs)
        badge = "ok" if f == 0 else "bad"
        rows.append(
            f"<tr><td>{ch}</td><td class='nm'>{CHAPTER_NAMES.get(ch,'')}</td>"
            f"<td>{len(rs)}</td><td class='{badge}'>{f}</td>"
            f"<td>{rev}</td><td>{p}</td></tr>")
    return f"""<!doctype html><meta charset="utf-8">
<title>ASVS L2 Audit Rollup — {run_date}</title>
<style>
 body{{font-family:Arial,Helvetica,sans-serif;margin:40px;color:#1a1a1a}}
 h1{{font-size:20px}} .sub{{color:#666;margin-bottom:20px}}
 table{{border-collapse:collapse;width:100%;font-size:14px}}
 th,td{{border:1px solid #ddd;padding:8px 10px;text-align:center}}
 th{{background:#0b3d5c;color:#fff}} td.nm{{text-align:left}}
 td.bad{{background:#f8d7da;font-weight:bold}} td.ok{{background:#d4edda}}
 tfoot td{{font-weight:bold;background:#eef}}
</style>
<h1>OWASP ASVS 4.0.3 — Level 2 Audit Rollup</h1>
<div class="sub">scope: {scope} &middot; run {run_date}</div>
<table>
<thead><tr><th>Chapter</th><th>Name</th><th>Assessed</th>
<th>Findings</th><th>Needs review</th><th>Pass/Resolved</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
<tfoot><tr><td colspan="2">TOTAL</td><td>{tot['assessed']}</td>
<td>{tot['findings']}</td><td>{tot['review']}</td><td>{tot['pass']}</td></tr></tfoot>
</table>"""


def main():
    run_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    doc = load()
    baseline_by_id = {r["req_id"]: r for r in doc["requirements"]}

    fpath = os.path.join("asvs-audit", "state", run_date, "findings.json")
    if not os.path.exists(fpath):
        sys.exit(f"no findings for run {run_date} at {fpath}")
    with open(fpath, encoding="utf-8") as f:
        run_doc = json.load(f)
    results = run_doc["results"]
    scope = run_doc.get("scope", "all")

    by_chapter = {}
    for r in results:
        # add-finding validates these, but a hand-edited findings.json might not;
        # skip with a warning rather than crash at the end of the run.
        if not r.get("chapter") or not r.get("status") or not r.get("req_id"):
            sys.stderr.write(
                f"warning: skipping malformed finding (need req_id/chapter/"
                f"status): {json.dumps(r)[:120]}\n")
            continue
        by_chapter.setdefault(r["chapter"], []).append(r)

    out_dir = os.path.join("asvs-audit", "reports", run_date)
    os.makedirs(out_dir, exist_ok=True)
    for ch, rs in by_chapter.items():
        md = chapter_report(ch, CHAPTER_NAMES.get(ch, ""), rs, baseline_by_id)
        with open(os.path.join(out_dir, f"{ch}.md"), "w", encoding="utf-8") as f:
            f.write(md)
    with open(os.path.join(out_dir, "rollup.html"), "w", encoding="utf-8") as f:
        f.write(rollup_html(by_chapter, run_date, scope))

    print(f"wrote {len(by_chapter)} chapter report(s) + rollup.html to {out_dir}")


if __name__ == "__main__":
    main()
