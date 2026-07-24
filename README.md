# mikegoodman.org

Personal website of Michael D. Goodman, Professor of Public Policy, UMass Dartmouth.

Static site: content lives in `data/*.json`, `build.py` renders it into HTML pages,
and GitHub Actions rebuilds and deploys automatically on every push to `main`.

## How to update the site

**Everything on the site comes from the JSON files in `data/`.** To update, edit the
relevant file (directly on github.com is fine — press `.` or use the pencil icon),
commit, and the site rebuilds itself in about a minute.

| To add or change… | Edit… |
|---|---|
| A journal article | `data/journal_articles.json` |
| An applied research report | `data/reports.json` |
| An op-ed | `data/opeds.json` |
| A media appearance | `data/media.json` (has `"year"` and `"text"` per item) |
| An invited talk | `data/talks.json` |
| A grant | `data/grants.json` |
| A board seat or advisory role | `data/service.json` |
| University service | `data/university_service.json` |
| Positions held | `data/experience.json` |

Most entries look like: `{"label": "2026", "text": "“Title,” Venue, year (with Coauthor)."}`
Copy an existing entry as a template and keep entries in reverse-chronological order.

## Updating from a new CV version

```
python3 parse_cv.py ~/Downloads/CV_MichaelDGoodman_Comprehensive_XXXX.docx
python3 build.py   # then commit and push
```

The downloadable CV is the Word-exported PDF, committed as
`MichaelGoodman-CV.pdf` in the repo root — replace that file (File > Save As >
PDF in Word) whenever the CV changes, alongside the data refresh.

`parse_cv.py` regenerates all CV-derived data files; it does not touch
`pdfmap.json`, `linkmap.json`, or `substack.json`. Counts shown on the site
(media citations, invited talks, reports, articles) are always computed from
the number of entries, so they can never drift out of sync.

## Attaching a PDF to an entry

1. Add the file to `pubs/` named `year-short-title.pdf`.
2. Add a line to `data/pdfmap.json` under the right section:
   `["unique phrase from the entry's text", "pubs/year-short-title.pdf"]`
The build matches the phrase against entry text and adds the PDF button automatically.

## Bio text and page copy

The About, Service, and Contact page prose lives in `build.py` (search for
`about_body`, `service_body`, `contact_body`).

## Local preview

```
python3 build.py && cd _site && python3 -m http.server 8000
```

Then open http://localhost:8000.
