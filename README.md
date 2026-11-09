# TCS Hiring Statement

Static site for the statement on hiring in theoretical computer science. Everything lives in `index.html`; there is no build step.

## Publish on GitHub Pages

1. Create a GitHub repository and push this folder to it.
2. In the repository, go to **Settings → Pages**, set **Source** to "Deploy from a branch", choose `main` and `/ (root)`, and save.
3. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.

## Adding signatories

Add one line per verified signatory inside `<ul class="signatories">` in `index.html`:

```html
<li>Jane Doe <span class="inst">Example University</span></li>
```

The count next to the heading updates automatically.
