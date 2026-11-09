# TCS Hiring Statement

Static site for the statement on hiring in theoretical computer science. Everything lives in `index.html`; there is no build step.

## Publish on GitHub Pages

1. Create a GitHub repository and push this folder to it.
2. In the repository, go to **Settings → Pages**, set **Source** to "Deploy from a branch", choose `main` and `/ (root)`, and save.
3. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.

## Updating signatories

The list lives in `signatories.csv` (columns: Timestamp, Name, University, Department). After editing it, rebuild the list on the page:

```sh
python3 update_signatories.py
```

The script drops duplicate names, sorts by last name, and rewrites the list in `index.html`. The count next to the heading updates automatically. Names whose last name isn't the final word (e.g. "François Le Gall") are listed in `SORT_AS` at the top of the script.
