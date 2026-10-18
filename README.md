# Inmailer

> Reliable CSS inlining for HTML email — follows the real CSS cascade, keeps what email clients need, and drops the rest.

<p align="center">
  <a href="https://pypi.org/project/inmailer/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/inmailer.svg"></a>
  <a href="https://pypi.org/project/inmailer/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/inmailer.svg"></a>
  <a href="https://github.com/AbdulWajid768/inmailer/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/AbdulWajid768/inmailer/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://pypi.org/project/inmailer/"><img alt="Downloads" src="https://img.shields.io/pypi/dm/inmailer.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/pypi/l/inmailer.svg"></a>
</p>

Most email clients ignore `<style>` blocks, so CSS has to be moved onto elements
as `style="..."` attributes. **Inmailer** does that for you — parsing your
stylesheets, inlining what it can following real CSS specificity, and keeping the
rest (`@media`, `@font-face`, `:hover`) in a single `<style>` tag.

## Features

- **Specificity-aware cascade** — more specific selectors and `!important` win,
  just like in a browser.
- **Preserves existing inline styles** as the highest-priority author styles.
- **Keeps non-inlineable CSS** (`@media`, `@font-face`, pseudo-classes) in a
  `<style>` tag instead of discarding it.
- **External stylesheets** — resolves `<link rel="stylesheet">` tags and inlines
  CSS from separate files.
- **Practical options** — strip classes, keep original `<style>` tags, and
  control output formatting.
- **Command-line interface** and file helpers.
- **Typed** (ships `py.typed`) and tested on Python 3.8–3.13.

## Installation

```bash
pip install inmailer
```

Requires Python 3.8 or newer.

## Quick start

```python
from inmailer import inline_css

html = """
<html>
  <head>
    <style>
      h1 { color: red; }
      #title { color: green; }                 /* more specific — wins */
      a:hover { text-decoration: underline; }  /* kept in <style> */
    </style>
  </head>
  <body><h1 id="title">Hello</h1></body>
</html>
"""

print(inline_css(html))
```

```html
<html>
  <head><style>a:hover { text-decoration: underline }</style></head>
  <body><h1 id="title" style="color: green">Hello</h1></body>
</html>
```

## Usage

### Options

`inline_css(html_content, extra_css=None, **options)` accepts:

| Option | Default | Description |
| --- | --- | --- |
| `extra_css` | `None` | Additional CSS string to inline (applied last). |
| `css_files` | `None` | Paths to external CSS files to read and inline. |
| `base_path` | `None` | Directory for resolving `<link>` hrefs and `css_files`. |
| `resolve_links` | `True` | Read and inline `<link rel="stylesheet">` tags. |
| `allow_remote` | `False` | Fetch `http(s)` stylesheet links over the network. |
| `encoding` | `"utf-8"` | Encoding for reading linked/external CSS. |
| `remove_classes` | `False` | Strip `class` attributes after inlining. |
| `keep_style_tags` | `False` | Also keep the original CSS in a `<style>` tag. |
| `pretty_print` | `True` | Indented output; set `False` for compact HTML. |

### External stylesheets

`<link rel="stylesheet">` tags are resolved and inlined automatically. Local
hrefs resolve against `base_path`; links that cannot be loaded are left in place.
You can also pass CSS files explicitly:

```python
inline_css(
    html,
    css_files=["theme.css", "overrides.css"],
    base_path="templates/",
    allow_remote=False,  # set True to fetch http(s) <link> stylesheets
)
```

### Working with files

```python
from inmailer import inline_css_file

# Relative <link href="..."> resolves next to newsletter.html automatically.
inline_css_file("newsletter.html", "newsletter.inlined.html", remove_classes=True)
```

### Command line

```bash
inmailer input.html -o output.html --remove-classes
inmailer input.html --css-file theme.css --css-file overrides.css
cat input.html | inmailer --compact > output.html
```

Run `inmailer --help` for all flags.

## How it works

1. Collect CSS from `<style>` tags, `<link>` stylesheets, `css_files`, and
   `extra_css`, in document order.
2. Classify each rule as inlineable or not (pseudo-classes, `@media`, and
   `@font-face` stay in a `<style>` tag).
3. Apply inlineable rules by cascade priority — `(!important, specificity,
   source order)` — so the winning declaration lands on each element.
4. Serialize the document back to HTML.

## Development

```bash
git clone https://github.com/AbdulWajid768/inmailer.git
cd inmailer
pip install -e .[test]
pytest
```

Contributions are welcome. Please open an issue or pull request, and keep changes
focused with tests where it makes sense.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

Released under the [MIT License](LICENSE).
