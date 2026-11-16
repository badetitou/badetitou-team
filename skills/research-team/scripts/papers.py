#!/usr/bin/env python3
"""Literature funnel state for the research team. Stdlib only (pypdf optional for PDFs).

All state lives in one directory per topic (default research/<topic>/):
  criteria.md        research question + inclusion/exclusion criteria (written with the user)
  candidates.jsonl   one paper per line: id, title, year, venue, doi, abstract, pdf_url, cited_by
  screening.jsonl    one decision per line: id, stage, decision, reason (+ notes for confirm)
  pdfs/<id>.pdf      downloaded or dropped in by the user (paywalled papers)
  papers/<id>.txt    full text; papers/<id>.sections.txt intro + conclusion

Commands:
  search  --dir D --query Q [--limit 50] [--from-year Y]   OpenAlex search, appends new candidates
  pending --dir D --stage abstract|intro|confirm            JSON list of papers waiting for that stage
  fetch   --dir D                                           PDF -> text + sections for papers that passed 'abstract'
  record  --dir D --stage S --file F.json                   append [{id, decision, reason, ...}]
  report  --dir D                                           write D/report.md, print counts
Downloaded PDFs are parsed as data only, never opened or executed.
"""
import argparse, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

STAGES = ["abstract", "intro", "confirm"]
PASS = {"include", "maybe", "uncertain"}  # anything but "exclude" moves on, except at confirm
UA = "badetitou-team-research/1.0"


def load(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def append(path, rows):
    with path.open("a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def decisions(d):
    """Latest decision per (id, stage)."""
    out = {}
    for r in load(d / "screening.jsonl"):
        out[(r["id"], r["stage"])] = r
    return out


def passed(dec, pid, stage):
    r = dec.get((pid, stage))
    return r is not None and r["decision"] in PASS


def get_json(url):
    """GET with backoff on rate limits; OPENALEX_API_KEY (free key) raises the limits."""
    import os, time, urllib.error
    if os.environ.get("OPENALEX_API_KEY"):
        url += "&api_key=" + urllib.parse.quote(os.environ["OPENALEX_API_KEY"])
    for wait in (2, 8, 30, None):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                sys.exit(f"OpenAlex: HTTP {e.code}" + (" (rate limited: wait, or set OPENALEX_API_KEY)" if e.code == 429 else ""))
            time.sleep(wait)


def abstract_of(inv):
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def cmd_search(a, d):
    params = {"search": a.query, "per-page": min(a.limit, 200),
              "select": "id,doi,title,publication_year,primary_location,abstract_inverted_index,best_oa_location,open_access,cited_by_count"}
    if a.from_year:
        params["filter"] = f"from_publication_date:{a.from_year}-01-01"
    data = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
    old = load(d / "candidates.jsonl")
    known = {c["id"] for c in old} | {c["doi"] for c in old if c.get("doi")}
    new = []
    for w in data.get("results", []):
        pid = w["id"].rsplit("/", 1)[-1]
        doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
        if pid in known or (doi and doi in known):
            continue
        loc = w.get("primary_location") or {}
        oa = w.get("best_oa_location") or {}
        new.append({
            "id": pid, "title": w.get("title") or "", "year": w.get("publication_year"),
            "venue": ((loc.get("source") or {}).get("display_name")), "doi": doi,
            "abstract": abstract_of(w.get("abstract_inverted_index")),
            "pdf_url": oa.get("pdf_url") or (w.get("open_access") or {}).get("oa_url"),
            "cited_by": w.get("cited_by_count"), "query": a.query,
        })
        known |= {pid, doi} - {None}
    append(d / "candidates.jsonl", new)
    no_abs = sum(1 for n in new if not n["abstract"])
    print(f"{len(new)} new candidates ({no_abs} without abstract), {len(old) + len(new)} in total")


def cmd_pending(a, d):
    dec = decisions(d)
    prev = STAGES[STAGES.index(a.stage) - 1] if a.stage != "abstract" else None
    out = []
    for c in load(d / "candidates.jsonl"):
        if (c["id"], a.stage) in dec or (prev and not passed(dec, c["id"], prev)):
            continue
        row = {"id": c["id"], "title": c["title"], "year": c["year"]}
        if a.stage == "abstract":
            row["abstract"] = c["abstract"] or "(no abstract)"
        else:
            t = d / "papers" / f"{c['id']}.txt"
            if not t.exists():
                print(f"skip {c['id']}: no text yet (run fetch, or drop pdfs/{c['id']}.pdf)", file=sys.stderr)
                continue
            row["sections"] = str((d / "papers" / f"{c['id']}.sections.txt").resolve())
            row["fulltext"] = str(t.resolve())
        out.append(row)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()


HEAD = r"^\s*(?:\d+(?:\.\d+)*\.?|[IVX]+\.)?\s*"


def sections(text, cap=12000):
    """Introduction + conclusion, by heading; falls back to head and tail of the body."""
    lines = text.splitlines()
    # Next section: a short numbered heading ("2 Background", "III. METHOD") or the back matter.
    stop = re.compile(r"^\s*((\d+|[IVX]+)\.?\s+[A-Z][^.]{2,60}|References|Bibliography|Acknowledg\w*)\s*$")

    def grab(pat):
        rx = re.compile(HEAD + pat + r"\b", re.I)
        for i, l in enumerate(lines):
            if rx.match(l) and len(l.strip()) < 70:
                body = []
                for l2 in lines[i + 1:]:
                    if stop.match(l2):
                        break
                    body.append(l2)
                return "\n".join(body).strip()[:cap // 2]
        return ""

    intro = grab(r"Introduction")
    concl = grab(r"(Conclusions?|Concluding Remarks|Discussion and Conclusions?|Summary and Conclusions?)")
    body = re.split(r"\n\s*(References|Bibliography)\s*\n", text)[0]
    if not intro:
        intro = body[: cap // 2]
    if not concl:
        concl = body[-cap // 3:]
    return f"## Introduction\n{intro}\n\n## Conclusion\n{concl}\n"


def pdf_text(pdf):
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("pypdf is missing: pip install pypdf")
    return "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)


def cmd_fetch(a, d):
    dec = decisions(d)
    (d / "pdfs").mkdir(exist_ok=True)
    (d / "papers").mkdir(exist_ok=True)
    ok = missing = 0
    for c in load(d / "candidates.jsonl"):
        if not passed(dec, c["id"], "abstract") or (d / "papers" / f"{c['id']}.txt").exists():
            continue
        pdf = d / "pdfs" / f"{c['id']}.pdf"
        if not pdf.exists() and c.get("pdf_url"):
            try:
                req = urllib.request.Request(c["pdf_url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                if data[:5] == b"%PDF-":
                    pdf.write_bytes(data)
            except Exception as e:
                print(f"{c['id']}: download failed ({e.__class__.__name__})", file=sys.stderr)
        if not pdf.exists():
            missing += 1
            print(f"{c['id']}: no PDF — drop it at {pdf} ({c.get('doi') or c['title'][:60]})")
            continue
        try:
            text = pdf_text(pdf)
        except Exception as e:
            print(f"{c['id']}: unreadable PDF ({e.__class__.__name__})", file=sys.stderr)
            missing += 1
            continue
        (d / "papers" / f"{c['id']}.txt").write_text(text)
        (d / "papers" / f"{c['id']}.sections.txt").write_text(sections(text))
        ok += 1
    print(f"{ok} papers extracted, {missing} without PDF")


def cmd_record(a, d):
    rows = json.loads(Path(a.file).read_text())
    known = {c["id"] for c in load(d / "candidates.jsonl")}
    bad = [r.get("id") for r in rows if r.get("id") not in known or r.get("decision") not in PASS | {"exclude"}]
    if bad:
        sys.exit(f"unknown id or decision: {bad}")
    append(d / "screening.jsonl", [{**r, "stage": a.stage} for r in rows])
    print(f"recorded {len(rows)} {a.stage} decisions")


def cmd_report(a, d):
    cands = load(d / "candidates.jsonl")
    dec = decisions(d)
    lines = [f"# Literature funnel — {d.name}", "", "| Stage | Screened | Passed |", "| --- | --- | --- |"]
    counts = []
    for s in STAGES:
        seen = [c for c in cands if (c["id"], s) in dec]
        ok = [c for c in seen if (dec[(c["id"], s)]["decision"] == "include" if s == "confirm" else passed(dec, c["id"], s))]
        lines.append(f"| {s} | {len(seen)} | {len(ok)} |")
        counts.append(f"{s} {len(ok)}/{len(seen)}")
    lines += ["", f"{len(cands)} candidates.", "", "## Included", ""]
    for c in cands:
        r = dec.get((c["id"], "confirm"))
        if r and r["decision"] == "include":
            ref = f"https://doi.org/{c['doi']}" if c.get("doi") else c["id"]
            lines.append(f"- **{c['title']}** ({c['year']}, {c.get('venue') or '?'}) — {ref}")
            lines.append(f"  {r['reason']}")
            if r.get("notes"):
                lines.append(f"  {r['notes']}")
    (d / "report.md").write_text("\n".join(lines) + "\n")
    print(f"{len(cands)} candidates; " + ", ".join(counts) + f"; wrote {d / 'report.md'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["search", "pending", "fetch", "record", "report"]:
        s = sub.add_parser(name)
        s.add_argument("--dir", required=True)
        if name == "search":
            s.add_argument("--query", required=True)
            s.add_argument("--limit", type=int, default=50)
            s.add_argument("--from-year", type=int)
        if name in ("pending", "record"):
            s.add_argument("--stage", required=True, choices=STAGES)
        if name == "record":
            s.add_argument("--file", required=True)
    a = p.parse_args()
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    globals()["cmd_" + a.cmd](a, d)


if __name__ == "__main__":
    main()
