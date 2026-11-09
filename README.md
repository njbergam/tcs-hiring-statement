# TCS Hiring Statement

Static site for the statement on hiring in theoretical computer science.

## Publish on GitHub Pages

1. Create a GitHub repository and push this folder to it.
2. In the repository, go to **Settings → Pages**, set **Source** to "Deploy from a branch", choose `main` and `/ (root)`, and save.
3. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.

## Editing the page

The text lives in Markdown files in `content/`:

| File | Section |
| --- | --- |
| `header.md` | Title (`# ...`) and subtitle |
| `intro.md` | Introduction |
| `statement.md` | The statement and its footnote |
| `sign.md` | Sign button (the link on its own line) and the text under it |
| `faq.md` | FAQ: each `## ` line is a question, followed by its answer |

Signatories live in `signatories.csv` (columns: Timestamp, Name, University, Department).

After editing, rebuild and preview:

```sh
python3 build.py
open index.html
```

Then commit and push, including the regenerated `index.html`. Don't edit `index.html` directly; it is overwritten on every build. Layout and styling are in `template.html`.

Markdown supported: paragraphs, numbered and bulleted lists, `**bold**`, `*italic*`, `[links](https://...)`, and footnotes (`[^1]` in the text plus a `[^1]: ...` line). Straight quotes become curly quotes automatically.

The build drops duplicate signatory names and sorts by last name. Names whose last name isn't the final word (e.g. "François Le Gall") are listed in `SORT_AS` at the top of `build.py`.
