#!/usr/bin/env python3
"""Regenerate data/*.json from the Word CV.

Usage:  python3 parse_cv.py /path/to/CV.docx

Rewrites the CV-derived data files (education, experience, awards,
journal_articles, book_chapters, reports, opeds, grants, media, talks,
university_service, service). Leaves pdfmap.json, linkmap.json, and
substack.json untouched. Run build.py afterwards.
"""
import sys, os, re, json, html, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))

def extract_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = []
    for p in re.findall(r"<w:p\b.*?</w:p>", xml, re.S):
        s = ""
        for m in re.finditer(r"(<w:tab/>)|<w:t(?:>| [^>]*>)(.*?)</w:t>", p, re.S):
            s += "\t" if m.group(1) else m.group(2)
        paras.append(html.unescape(s))
    return paras

SECTIONS = {   # heading text (normalized) -> key
    "EDUCATION": "education",
    "PROFESSIONAL EXPERIENCE": "experience",
    "AWARDS AND HONORS": "awards",
    "JOURNAL ARTICLES": "journal_articles",
    "BOOK CHAPTERS": "book_chapters",
    "APPLIED RESEARCH REPORTS": "reports",
    "OPINION PIECES": "opeds",
    "GRANT & CONTRACT FUNDING": "grants",
    "MEDIA APPEARANCES": "media",
    "MEDIA ENGAGEMENT": "media",
    "INVITED TALKS AND PRESENTATIONS": "talks",
    "UNIVERSITY SERVICE": "university_service",
    "SELECTED PROFESSIONAL AND PUBLIC SERVICE ACTIVITIES": "service",
}

def split_sections(lines):
    out, current = {}, None
    for l in lines:
        key = SECTIONS.get(re.sub(r"\s+", " ", l).strip().upper())
        if key:
            current = key
            out.setdefault(current, [])
        elif current:
            out[current].append(l)
    return out

def tabbed(lines):
    out = []
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if "\t" in l:
            k, v = l.split("\t", 1)
            out.append({"label": k.strip(), "text": re.sub(r"\s+", " ", v).strip()})
        elif out:
            out[-1]["text"] += " " + re.sub(r"\s+", " ", l).strip()
    return out

def parse(docx_path):
    lines = extract_paragraphs(docx_path)
    sec = split_sections(lines)
    data = {}
    data["education"] = tabbed(sec["education"])
    exp, employer = [], None
    for l in sec["experience"]:
        if not l.strip():
            continue
        if "\t" not in l:
            employer = l.strip()
            continue
        k, v = l.split("\t", 1)
        v = re.sub(r"\s+", " ", v).strip()
        if not v and exp:                       # continuation year line
            exp[-1]["years"] += "; " + k.strip()
        else:
            exp.append({"years": k.strip().rstrip(";").strip(), "role": v, "org": employer})
    data["experience"] = [e for e in exp if e["role"]]
    data["awards"] = tabbed(sec["awards"])
    data["journal_articles"] = tabbed(sec["journal_articles"])
    data["book_chapters"] = tabbed(sec["book_chapters"])
    data["reports"] = tabbed(sec["reports"])
    data["opeds"] = tabbed(sec["opeds"])
    g_lines = sec["grants"]
    total = next((re.search(r"\$[\d,]+", l).group(0) for l in g_lines
                  if l.strip().startswith("Total") and re.search(r"\$[\d,]+", l)), "")
    g_items = tabbed([l for l in g_lines
                      if l.strip() and not l.strip().startswith(("Total", "External Funding"))])
    data["grants"] = {"total": total, "items": g_items}
    media, yr, intro = [], None, None
    for l in sec["media"]:
        l = l.strip()
        if not l:
            continue
        if re.fullmatch(r"(19|20)\d\d", l):
            yr = l
            continue
        if intro is None and l.startswith("My research"):
            intro = l
            continue
        media.append({"year": yr, "text": re.sub(r"\s+", " ", l)})
    data["media"] = {"intro": intro, "items": media}
    talks = []
    for e in tabbed(sec["talks"]):
        m = re.match(r"(\d{2})/(\d{2})/(\d{2})", e["label"])
        talks.append({"date": e["label"], "year": ("20" + m.group(3)) if m else e["label"],
                      "text": e["text"]})
    data["talks"] = talks
    data["university_service"] = [l.strip() for l in sec["university_service"] if l.strip()]
    data["service"] = tabbed(sec["service"])
    return data

def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 parse_cv.py /path/to/CV.docx")
    data = parse(sys.argv[1])
    for k, v in data.items():
        path = os.path.join(ROOT, "data", k + ".json")
        with open(path, "w") as f:
            json.dump(v, f, indent=1, ensure_ascii=False)
        n = len(v) if isinstance(v, list) else len(v.get("items", []))
        print(f"{k}: {n}")

if __name__ == "__main__":
    main()
