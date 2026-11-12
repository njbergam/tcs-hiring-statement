#!/usr/bin/env python3
"""Build index.html from template.html, the Markdown files in content/, and signatories.csv.

Usage:  python3 build.py

Edit the files in content/ (and signatories.csv), then run this script and
open index.html to preview. Don't edit index.html directly; it is overwritten.

Supported Markdown (kept deliberately small):
  - Paragraphs separated by a blank line
  - Numbered lists ("1. ...") and bulleted lists ("- ...")
  - ## Headings (in faq.md, each "## " line is a question)
  - **bold**, *italic*, [link text](https://...)
  - Footnotes: [^1] in the text, and a line "[^1]: footnote text"
  - Straight quotes and apostrophes are turned into curly ones automatically.
"""
import csv
import datetime
import html
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENT = HERE / "content"

# Signatories whose sort key isn't simply the last word of their name.
SORT_AS = {
    "Ronald de Wolf": "Wolf",
    "François Le Gall": "Le Gall",
    "Bhaskar Ray Chaudhury": "Ray Chaudhury",
    "Shayan Oveis Gharan": "Oveis Gharan",
}


# ---------- inline Markdown ----------

LINK = re.compile(r"\[([^\]^][^\]]*)\]\(([^)\s]+)\)")
FOOTREF = re.compile(r"\[\^(\w+)\]")


def smart_quotes(text):
    text = re.sub(r"(^|[\s(\[{\u2014-])'", "\\1\u2018", text)
    text = text.replace("'", "\u2019")
    text = re.sub(r'(^|[\s(\[{\u2014-])"', "\\1\u201c", text)
    return text.replace('"', "\u201d")


def inline(text):
    links = []

    def stash_link(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00L{len(links) - 1}\x00"

    text = LINK.sub(stash_link, text)
    text = FOOTREF.sub(lambda m: f"\x00F{m.group(1)}\x00", text)
    text = smart_quotes(html.escape(text, quote=False))
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\x00F(\w+)\x00", r"<sup>\1</sup>", text)

    def restore_link(m):
        label, url = links[int(m.group(1))]
        return f'<a href="{html.escape(url)}">{inline(label)}</a>'

    return re.sub(r"\x00L(\d+)\x00", restore_link, text)


# ---------- block Markdown ----------

def blocks(md):
    """Split Markdown into (kind, payload) blocks."""
    out = []
    for chunk in re.split(r"\n\s*\n", md.strip()):
        lines = [l.rstrip() for l in chunk.splitlines() if l.strip()]
        first = lines[0]
        if first.startswith("#"):
            level = len(first) - len(first.lstrip("#"))
            out.append(("h", (level, first[level:].strip())))
            if lines[1:]:
                out.append(("p", " ".join(l.strip() for l in lines[1:])))
        elif re.match(r"\[\^\w+\]:", first):
            for l in lines:
                m = re.match(r"\[\^(\w+)\]:\s*(.*)", l)
                if m:
                    out.append(("fn", (m.group(1), m.group(2))))
                elif out:
                    k, (n, t) = out[-1]
                    out[-1] = (k, (n, t + " " + l.strip()))
        elif re.match(r"(\d+\.|[-*])\s", first):
            ordered = first[0].isdigit()
            items = []
            for l in lines:
                m = re.match(r"\s*(\d+\.|[-*])\s+(.*)", l)
                if m:
                    items.append(m.group(2))
                else:
                    items[-1] += " " + l.strip()
            out.append(("ol" if ordered else "ul", items))
        else:
            out.append(("p", " ".join(l.strip() for l in lines)))
    return out


def render(blist, indent=4, first_p_class=None):
    pad = " " * indent
    html_out = []
    for kind, val in blist:
        if kind == "p":
            cls = ""
            if first_p_class and not any(k == "p" for k, _ in blist[: blist.index((kind, val))]):
                cls = f' class="{first_p_class}"'
            html_out.append(f"{pad}<p{cls}>{inline(val)}</p>")
        elif kind in ("ol", "ul"):
            items = "\n".join(f"{pad}  <li>{inline(i)}</li>" for i in val)
            html_out.append(f"{pad}<{kind}>\n{items}\n{pad}</{kind}>")
        elif kind == "h":
            level, text = val
            html_out.append(f"{pad}<h{level}>{inline(text)}</h{level}>")
    return "\n".join(html_out)


def read(name):
    return blocks((CONTENT / name).read_text(encoding="utf-8"))


# ---------- sections ----------

def build_header():
    b = read("header.md")
    title = next(v[1] for k, v in b if k == "h")
    subtitle = " ".join(v for k, v in b if k == "p")
    return f"<h1>{inline(title)}</h1>\n  <p class=\"subtitle\">{inline(subtitle)}</p>"


def build_statement():
    b = read("statement.md")
    body = [x for x in b if x[0] != "fn"]
    notes = "\n".join(
        f'    <p class="footnote"><sup>{n}</sup> {inline(t)}</p>' for k, (n, t) in
        ((k, v) for k, v in b if k == "fn")
    )
    return render(body, indent=6, first_p_class="lead"), notes


def build_sign():
    out = []
    for kind, val in read("sign.md"):
        m = LINK.fullmatch(val) if kind == "p" else None
        if m and not any('class="button"' in o for o in out):
            out.append(
                f'    <a class="button" href="{html.escape(m.group(2))}" '
                f'target="_blank" rel="noopener">{inline(m.group(1))}</a>'
            )
        else:
            out.append(render([(kind, val)]))
    return "\n".join(out)


def build_faq():
    parts, answers = [], []

    def flush():
        if answers:
            parts.append("      <dd>" + "".join(answers) + "</dd>")
            answers.clear()

    for kind, val in read("faq.md"):
        if kind == "h":
            flush()
            parts.append(f"\n      <dt>{inline(val[1])}</dt>")
        else:
            answers.append(render([(kind, val)], indent=0))
    flush()
    return "    <dl>" + "\n".join(parts) + "\n    </dl>"


def sort_key(name):
    last = SORT_AS.get(name, name.split()[-1])
    plain = unicodedata.normalize("NFKD", f"{last} {name}")
    return "".join(c for c in plain if not unicodedata.combining(c)).casefold()


def build_signatories():
    seen, people = set(), []
    with (HERE / "signatories.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("Name") or "").strip()
            if not name or name.casefold() in seen:
                continue
            seen.add(name.casefold())
            people.append((name, (row.get("University") or "").strip()))
    people.sort(key=lambda p: sort_key(p[0]))
    items = "\n".join(
        f'      <li>{html.escape(n)} <span class="inst">{html.escape(u)}</span></li>'
        for n, u in people
    )
    return items, len(people)


def main():
    statement, footnotes = build_statement()
    signatories, count = build_signatories()
    values = {
        "header": build_header(),
        "intro": render(read("intro.md")),
        "statement": statement,
        "statement_footnotes": footnotes,
        "sign": build_sign(),
        "faq": build_faq(),
        "signatories": signatories,
        "count": str(count),
        "updated": datetime.date.today().strftime("%B %Y"),
    }
    page = (HERE / "template.html").read_text(encoding="utf-8")
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{\w+\}\}", page)
    if leftover:
        raise SystemExit(f"Unfilled placeholders in template.html: {leftover}")
    page = page.replace(
        "<!doctype html>",
        "<!doctype html>\n<!-- Generated by build.py from template.html and content/. "
        "Edit those files and run: python3 build.py -->",
        1,
    )
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"Built index.html ({count} signatories)")


if __name__ == "__main__":
    main()
