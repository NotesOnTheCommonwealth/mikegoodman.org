#!/usr/bin/env python3
"""Static site generator for mikegoodman.org.

Reads data/*.json, writes finished HTML pages into _site/.
No dependencies beyond the Python standard library.
Run:  python3 build.py
"""
import json, os, shutil, html, re, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")

def asset_v(name):
    with open(os.path.join(ROOT, "assets", name), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]
CSS_V = asset_v("style.css")
JS_V = asset_v("site.js")

def load(name):
    with open(os.path.join(ROOT, "data", name + ".json")) as f:
        return json.load(f)

D = {n: load(n) for n in ["education","experience","awards","journal_articles",
     "book_chapters","reports","opeds","grants","media","talks",
     "university_service","service"]}
PDFMAP = load("pdfmap")

def fetch_substack():
    """Refresh data/substack.json from the live feed; fall back to the committed cache."""
    try:
        import urllib.request, xml.etree.ElementTree as ET, email.utils
        req = urllib.request.Request("https://commonwealthnotes.substack.com/feed",
                                     headers={"User-Agent": "mikegoodman.org site build"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=10).read())
        posts = []
        for item in root.find("channel").findall("item")[:5]:
            d = email.utils.parsedate_to_datetime(item.findtext("pubDate"))
            posts.append({"title": item.findtext("title"),
                          "subtitle": (item.findtext("description") or "").strip(),
                          "date": d.strftime("%B %-d, %Y"),
                          "link": item.findtext("link")})
        if posts:
            with open(os.path.join(ROOT, "data", "substack.json"), "w") as f:
                json.dump({"posts": posts}, f, indent=1, ensure_ascii=False)
    except Exception as e:
        print("substack feed unavailable, using cached copy:", e)
    return load("substack")

SUBSTACK = fetch_substack()

def esc(s): return html.escape(s, quote=False)

def pdf_for(section, text):
    for needle, path in PDFMAP.get(section, []):
        if needle.lower() in text.lower():
            return path
    return None

def entry_li(label, text, section=None, wide=False):
    body = esc(text)
    pdf = pdf_for(section, text) if section else None
    btn = f' <a class="pdfbtn" href="{pdf}">PDF</a>' if pdf else ""
    return f'<li><span class="yr">{esc(label)}</span><span class="t">{body}{btn}</span></li>'

def entries(items, section=None, first=None, wide=False, label_key="label", text_key="text"):
    cls = "entries wide" if wide else "entries"
    attr = f' data-first="{first}"' if first else ""
    lis = "\n".join(entry_li(i[label_key], i[text_key], section) for i in items)
    return f'<ul class="{cls}"{attr}>\n{lis}\n</ul>'

NAV = [("index.html","About"),("cv.html","Curriculum Vitae"),
       ("publications.html","Publications"),("media.html","In the Media"),
       ("service.html","Public & Board Service"),("contact.html","Contact")]

def shell(active, title, body, desc):
    ACT = ' class="active"'
    nav = "\n".join(
        f'<a href="{href}"{ACT if href==active else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css?v={CSS_V}">
</head>
<body>
<div class="masthead">
  <h1><a href="index.html">Michael D. Goodman, Ph.D.</a></h1>
  <p class="role">Professor of Public Policy &middot; University of Massachusetts Dartmouth</p>
</div>
<div class="rule2"></div>
<nav class="mainnav">
{nav}
</nav>
<main class="page">
{body}
</main>
<footer>&copy; 2026 Michael D. Goodman &middot; mikegoodman.org</footer>
<script src="assets/site.js?v={JS_V}"></script>
</body>
</html>"""

# ---------- About ----------
about_body = f"""
<div class="about-grid">
  <div>
    <p style="margin-top:0">Michael D. Goodman is Professor of Public Policy at the University of Massachusetts Dartmouth and, since 2001, co-editor of <i>MassBenchmarks</i>, the journal of the Massachusetts economy published by the UMass Donahue Institute in collaboration with the Federal Reserve Bank of Boston.</p>
    <p>An economic sociologist by training (Ph.D., Boston University), his research and commentary focus on economic development, housing, coastal resilience, and the workforce challenges facing Massachusetts and New England. His work has been supported by more than $13.8 million in external funding, and his analysis has been cited in more than 680 print, radio, and television stories since 2002.</p>
    <p>At UMass Dartmouth he has served as Acting Provost &amp; Vice Chancellor for Academic Affairs, Senior Advisor to the Chancellor for Economic Development &amp; Strategic Initiatives, and Executive Director of Economic Development &amp; Community Partnerships. He previously directed the university's Public Policy Center and chaired the Department of Public Policy.</p>
    <p>He serves as a Public Director of the Depositors Insurance Fund, on the Advisory Board of the Federal Reserve Bank of Boston's New England Public Policy Center, and the Board of Economic Advisors of Associated Industries of Massachusetts, and — by gubernatorial appointment across three administrations — on the Commonwealth's Economic Assistance Coordinating Council.</p>
    <h2 class="sec">Selected Recent Work</h2>
    <ul class="worklist">
      <li><span class="w-note">In press · 2026</span><br>“Advancing the North Shore Blue Economy Initiative,” <span class="w-venue">The Northeastern Geographer</span> (with K. Kahl and D. Borges)</li>
      <li><span class="w-note">Funded initiative · 2024–26</span><br>Blue Economy Initiatives, Massachusetts Division of Marine Fisheries ($8.0M)</li>
      <li><span class="w-note">Commentary · 2025</span><br>Analysis featured in <span class="w-venue">CommonWealth Beacon</span> coverage of the Commonwealth's November economic check-in</li>
    </ul>
    <h2 class="sec">Notes on the Commonwealth</h2>
    <p class="sec-sub">Periodic commentary on the people, places, public affairs, and economy of Massachusetts — <a href="https://commonwealthnotes.substack.com">subscribe on Substack</a>.</p>
    <ul class="worklist">
""" + "\n".join(
    f'      <li><span class="w-note">{p["date"]}</span><br><a href="{p["link"]}">{html.escape(p["title"], quote=False)}</a>'
    + (f' — <span class="w-venue">{html.escape(p["subtitle"], quote=False)}</span>' if p["subtitle"] else "")
    + "</li>"
    for p in SUBSTACK["posts"][:3]) + """
    </ul>
  </div>
  <div class="aside">
    <img class="headshot" src="assets/headshot.jpg" alt="Michael D. Goodman">
    <div class="sidecard">
      <b>Department of Public Policy</b><br>
      University of Massachusetts Dartmouth<br>
      285 Old Westport Road<br>
      Dartmouth, MA 02747<br><br>
      <a href="mailto:mgoodman@umassd.edu">mgoodman@umassd.edu</a><br>
      617.823.2770
    </div>
  </div>
</div>"""

# ---------- CV ----------
exp_by_org = {}
for e in D["experience"]:
    exp_by_org.setdefault(e["org"], []).append(e)
exp_html = ""
for org, items in exp_by_org.items():
    lis = "\n".join(f'<li><span class="yr">{esc(i["years"])}</span><span class="t">{esc(i["role"])}</span></li>' for i in items)
    exp_html += f'<p class="count">{esc(org)}</p>\n<ul class="entries">\n{lis}\n</ul>\n'

grants = D["grants"]
uni = "\n".join(f"<li>{esc(x)}</li>" for x in D["university_service"])
cv_body = f"""
<div class="cv-head">
  <h2 class="sec">Curriculum Vitae</h2>
  <span><a class="btn" href="cv.html" onclick="window.print();return false;">Print / Save PDF</a></span>
</div>
<div class="cv-grid">
  <nav class="cv-side">
    <a href="#edu">Education</a>
    <a href="#exp">Experience</a>
    <a href="#awards">Awards &amp; Honors</a>
    <a href="#grants">Grants &amp; Contracts</a>
    <a href="#talks">Invited Talks</a>
    <a href="#uniservice">University Service</a>
    <a href="publications.html">Publications →</a>
    <a href="media.html">In the Media →</a>
    <a href="service.html">Public &amp; Board Service →</a>
  </nav>
  <div>
    <section class="cvsec" id="edu">
      <h3>Education</h3>
      {entries(D["education"])}
    </section>
    <section class="cvsec" id="exp">
      <h3>Professional Experience</h3>
      {exp_html}
    </section>
    <section class="cvsec" id="awards">
      <h3>Awards &amp; Honors</h3>
      {entries(D["awards"])}
    </section>
    <section class="cvsec" id="grants">
      <h3>Grants &amp; Contract Funding</h3>
      <p class="count">{esc(grants["total"])} in external funding as principal or co-principal investigator</p>
      {entries(grants["items"], first=8, wide=True)}
    </section>
    <section class="cvsec" id="talks">
      <h3>Invited Talks &amp; Presentations</h3>
      <p class="count">{len(D["talks"])} invited talks, keynotes, and testimony since 2002</p>
      {entries(D["talks"], first=10, label_key="date")}
    </section>
    <section class="cvsec" id="uniservice">
      <h3>University Service</h3>
      <ul class="entries plain" data-first="8">
        {uni}
      </ul>
    </section>
  </div>
</div>"""

# ---------- Publications ----------
pubs_body = f"""
<h2 class="sec">Publications</h2>
<p class="sec-sub">Peer-reviewed articles, book chapters, applied research reports, and public commentary. Entries marked <span class="pdfbtn" style="cursor:default">PDF</span> link to the full document.</p>
<section class="cvsec">
  <h3>Journal Articles</h3>
  <p class="count">{len(D["journal_articles"])} peer-reviewed articles, 1993–2026</p>
  {entries(D["journal_articles"], section="journal_articles", first=7)}
</section>
<section class="cvsec">
  <h3>Book Chapters</h3>
  {entries(D["book_chapters"], section="book_chapters")}
</section>
<section class="cvsec">
  <h3>Applied Research Reports</h3>
  <p class="count">{len(D["reports"])} reports for federal and state agencies, municipalities, foundations, and industry</p>
  {entries(D["reports"], section="reports", first=8)}
</section>
<section class="cvsec">
  <h3>Opinion Pieces</h3>
  <p class="count">{len(D["opeds"])} op-eds in the Boston Globe, CommonWealth, and regional papers</p>
  {entries(D["opeds"], section="opeds", first=6)}
</section>"""

# ---------- Media ----------
media = D["media"]
years = sorted({i["year"] for i in media["items"] if i["year"]}, reverse=True)
chip_html = '<button class="chip on" data-yr="all">All</button>' + "".join(
    f'<button class="chip" data-yr="{y}">{y}</button>' for y in years)
media_lis = "\n".join(
    f'<li data-yr="{i["year"]}"><span class="yr">{i["year"]}</span><span class="t">{esc(i["text"])}</span></li>'
    for i in media["items"])
media_body = f"""
<h2 class="sec">In the Media</h2>
<p class="sec-sub">{esc(media["intro"])}</p>
<div class="chips" id="yrchips">{chip_html}</div>
<ul class="entries" id="medialist" data-first="15">
{media_lis}
</ul>"""

# ---------- Service ----------
def svc(pred):
    return [s for s in D["service"] if pred(s)]
current = [s for s in D["service"] if s["label"].strip().endswith(("Present","–","-"))]
past = [s for s in D["service"] if s not in current]
service_body = f"""
<h2 class="sec">Public &amp; Board Service</h2>
<p class="sec-sub">Advisory appointments, board service, and public engagement across government, civic, and financial institutions.</p>
<section class="cvsec">
  <h3>Standing Appointments</h3>
  {entries(current, wide=True)}
</section>
<section class="cvsec">
  <h3>Past Board &amp; Advisory Service</h3>
  {entries(past, wide=True)}
</section>
<section class="cvsec">
  <h3>Testimony &amp; Board Briefings</h3>
  <p>A regular invited witness at the Massachusetts Legislature's annual consensus revenue hearings, he also briefs the boards of banks, chambers of commerce, and civic organizations on the economic outlook — in recent years including HarborOne Bank, Webster Bank, South Shore Bank, Bank Five, Reading Cooperative Bank, and the Society of Municipal Analysts.</p>
  <p>He welcomes conversations about board and advisory service. <a href="contact.html">Contact</a></p>
</section>"""

# ---------- Contact ----------
contact_body = """
<h2 class="sec">Contact</h2>
<p>Department of Public Policy<br>
University of Massachusetts Dartmouth<br>
285 Old Westport Road, Dartmouth, MA 02747</p>
<p><a href="mailto:mgoodman@umassd.edu">mgoodman@umassd.edu</a> &middot; 617.823.2770</p>
<p><a href="https://commonwealthnotes.substack.com">Notes on the Commonwealth</a> — his Substack newsletter on the people, places, public affairs, and economy of Massachusetts.</p>
<p class="sec-sub">For media queries, speaking requests, board and advisory inquiries, and research collaboration.</p>"""

PAGES = {
 "index.html": ("index.html","Michael D. Goodman, Ph.D.",about_body,
    "Michael D. Goodman, Professor of Public Policy at UMass Dartmouth — economic development, housing, and the Massachusetts economy."),
 "cv.html": ("cv.html","Curriculum Vitae — Michael D. Goodman",cv_body,
    "Curriculum vitae of Michael D. Goodman, Professor of Public Policy, UMass Dartmouth."),
 "publications.html": ("publications.html","Publications — Michael D. Goodman",pubs_body,
    "Journal articles, book chapters, applied research reports, and op-eds by Michael D. Goodman."),
 "media.html": ("media.html","In the Media — Michael D. Goodman",media_body,
    "Media appearances and citations of Michael D. Goodman's research and commentary since 2002."),
 "service.html": ("service.html","Public & Board Service — Michael D. Goodman",service_body,
    "Advisory appointments and board service of Michael D. Goodman."),
 "contact.html": ("contact.html","Contact — Michael D. Goodman",contact_body,
    "Contact Michael D. Goodman, Professor of Public Policy, UMass Dartmouth."),
}

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    for fname,(active,title,body,desc) in PAGES.items():
        with open(os.path.join(OUT,fname),"w") as f:
            f.write(shell(active,title,body,desc))
    shutil.copytree(os.path.join(ROOT,"assets"), os.path.join(OUT,"assets"))
    if os.path.isdir(os.path.join(ROOT,"pubs")):
        shutil.copytree(os.path.join(ROOT,"pubs"), os.path.join(OUT,"pubs"))
    print("built", len(PAGES), "pages ->", OUT)

if __name__ == "__main__":
    main()
