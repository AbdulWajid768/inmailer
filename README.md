<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║  ░▒▓  INMAILER  ▓▒░                                               ║
║  HTML email CSS · inline engine · inbox-safe output               ║
╚══════════════════════════════════════════════════════════════════╝
```

[![PyPI](https://img.shields.io/badge/PyPI-inmailer-3776AB?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/inmailer/)
[![Python](https://img.shields.io/badge/Python-3.6+-00d4aa?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-7c3aed?style=for-the-badge)](LICENSE)

**Turn styled HTML into email-client-ready markup—automatically.**

[Install](#-install) · [Usage](#-usage) · [How it works](#-how-it-works)

</div>

---

## ◈ Signal

Email clients strip `<style>` blocks and ignore half your CSS. **Inmailer** parses in-document styles, inlines what clients understand, and preserves the rest (`@media`, `:hover`, `@font-face`) in a rebuilt `<style>` tag.

One function. Predictable output. Fewer broken newsletters.

---

## ◈ Install

```bash
pip install inmailer
```

Or from source:

```bash
git clone https://github.com/AbdulWajid768/inmailer.git
cd inmailer && pip install -e .
```

**Dependencies:** `lxml`, `cssutils`, `cssselect`

---

## ◈ Usage

```python
from inmailer import inline_css

html_content = """
<html>
  <head>
    <style>
      h1 { color: #00d4aa; font-size: 24px; }
      a:hover { text-decoration: underline; }
      @media (max-width: 600px) { .wrap { padding: 8px; } }
    </style>
  </head>
  <body>
    <h1>Hello, inbox</h1>
  </body>
</html>
"""

processed = inline_css(html_content)
print(processed)
```

**Result:** `h1` gets inline `style=…`; `:hover` and `@media` rules stay in `<head><style>`.

---

## ◈ How it works

```text
  HTML + <style>          parse (cssutils)
        │                      │
        ▼                      ▼
  classify rules ──► inlineable (no pseudo-selectors)
        │                      │
        │                      ├── match via CSSSelector (lxml)
        │                      └── merge into element style=""
        │
        └── non-inlineable (@media, @font-face, :hover, …)
                    └── re-insert single <style> in <head>
```

| Capability | Status |
| --- | --- |
| Inline class/element rules | ✓ |
| Preserve `@media` queries | ✓ |
| Preserve pseudo-classes (`:hover`, etc.) | ✓ |
| `!important` override semantics | ✓ |
| Graceful skip on malformed CSS | ✓ |

---

## ◈ Contributing

1. Fork → branch → commit → PR  
2. Keep changes focused; match existing style in `inmailer/core.py`.

---

## ◈ Maintainer

**[Abdul Wajid](https://github.com/AbdulWajid768)** · [abdul45.wajid@gmail.com](mailto:abdul45.wajid@gmail.com)

[![GitHub](https://img.shields.io/badge/@AbdulWajid768-181717?style=flat&logo=github)](https://github.com/AbdulWajid768)

---

<div align="center">

<sub>Style in the lab. Render in the inbox.</sub>

</div>
