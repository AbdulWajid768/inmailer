<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,40:00d4aa,100:16213e&height=200&section=header&text=INMAILER&fontSize=52&fontColor=ffffff&animation=twinkling&desc=CSS+%E2%86%92+inline+%7C+inbox-safe+HTML&descSize=16&descAlignY=72&descAlign=62"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=17&duration=2600&pause=800&color=00D4AA&center=true&vCenter=true&multiline=true&repeat=true&width=640&height=88&lines=Inline+what+Gmail+will+keep;Preserve+%40media+%2B+%3Ahover;Specificity-aware+cascade;Built+for+newsletters+%26+transactional" alt="Typing animation"/>
</a>

<br/>

### ⟡ Live telemetry ⟡

[![GitHub stars](https://img.shields.io/github/stars/AbdulWajid768/inmailer?style=for-the-badge&logo=starship&logoColor=white&labelColor=0f172a&color=00d4aa)](https://github.com/AbdulWajid768/inmailer/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AbdulWajid768/inmailer?style=for-the-badge&logo=git&logoColor=white&labelColor=0f172a&color=0891b2)](https://github.com/AbdulWajid768/inmailer/network/members)
[![PyPI version](https://img.shields.io/pypi/v/inmailer?style=for-the-badge&logo=pypi&logoColor=white&labelColor=0f172a&color=7c3aed)](https://pypi.org/project/inmailer/)
[![PyPI downloads](https://img.shields.io/pypi/dm/inmailer?style=for-the-badge&logo=python&logoColor=white&labelColor=0f172a&color=f472b6)](https://pypi.org/project/inmailer/)
[![License](https://img.shields.io/github/license/AbdulWajid768/inmailer?style=for-the-badge&logo=opensourceinitiative&logoColor=white&labelColor=0f172a&color=00d4aa)](LICENSE)

[![Last commit](https://img.shields.io/github/last-commit/AbdulWajid768/inmailer?style=for-the-badge&logo=git&logoColor=white&labelColor=0f172a&color=00d4aa)](https://github.com/AbdulWajid768/inmailer/commits/main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/AbdulWajid768/inmailer?style=for-the-badge&logo=pulse&logoColor=white&labelColor=0f172a&color=0891b2)](https://github.com/AbdulWajid768/inmailer/graphs/commit-activity)
[![Repo size](https://img.shields.io/github/repo-size/AbdulWajid768/inmailer?style=for-the-badge&logo=harddrive&logoColor=white&labelColor=0f172a&color=7c3aed)](https://github.com/AbdulWajid768/inmailer)

<br/>

<img src="assets/stats-pin.svg" alt="Repo stats" width="48%"/>
<img src="assets/stats-top-langs.svg" alt="Top languages" width="48%"/>

<br/><br/>

[📦 Install](#-install) · [⚡ Usage](#-usage) · [🔬 Engine](#-engine)

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=4,5,6&height=2&section=footer" width="100%"/>

</div>

---

## ◈ Transmission

Email clients **amputate** your `<style>` blocks. **Inmailer** rewrites HTML for the inbox era: parse document CSS, **inline** what survives (following the real CSS cascade — specificity and `!important` win), and **rehydrate** `@media`, `@font-face`, and pseudo-rules into a single `<style>` in `<head>`.

```text
   HTML + <style>  ──►  cssutils parse  ──►  rule classifier
                              │                    │
                              │         ┌──────────┴──────────┐
                              │         ▼                     ▼
                              │    inlineable            non-inlineable
                              │    (lxml match)          (re-insert <style>)
                              ▼
                        inbox-ready markup
```

---

## ◈ Install

```bash
pip install inmailer
```

Requires **Python 3.8+**.

```bash
git clone https://github.com/AbdulWajid768/inmailer.git
cd inmailer && pip install -e .[test]
```

**Stack:** `lxml` · `cssutils` · `cssselect`

---

## ◈ Usage

```python
from inmailer import inline_css

html_content = """
<html>
  <head>
    <style>
      h1 { color: red; }
      #title { color: green; }            /* more specific -> wins */
      a:hover { text-decoration: underline; }  /* kept in <style> */
      @media (max-width: 600px) { .wrap { padding: 8px; } }
    </style>
  </head>
  <body><h1 id="title">Hello, inbox</h1></body>
</html>
"""

print(inline_css(html_content))
```

### Options

```python
inline_css(
    html_content,
    extra_css="p { font-size: 14px; }",  # inline CSS from a separate source
    remove_classes=True,                 # strip class="" after inlining
    keep_style_tags=False,               # also keep the original <style> block
    pretty_print=True,                   # set False for compact output
)
```

### Work with files

```python
from inmailer import inline_css_file

inline_css_file("newsletter.html", "newsletter.inlined.html", remove_classes=True)
```

### Command line

```bash
inmailer input.html -o output.html --remove-classes
cat input.html | inmailer --compact > output.html
```

---

## ◈ Engine

| Capability | Status |
| --- | --- |
| Inline element/class/id rules | ✓ |
| Specificity-aware cascade | ✓ |
| `!important` merge logic | ✓ |
| Preserve existing inline styles | ✓ |
| Preserve `@media` / `@font-face` | ✓ |
| Preserve `:hover` / pseudo | ✓ |
| Inline extra CSS (`extra_css`) | ✓ |
| CLI + file helper | ✓ |
| Malformed CSS → skip gracefully | ✓ |

---

## ◈ Contributing

Fork → branch → `pip install -e .[test]` → `pytest` → PR. Keep changes surgical in `inmailer/core.py`.

---

<div align="center">

<a href="https://star-history.com/#AbdulWajid768/inmailer&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=AbdulWajid768/inmailer&type=Date&theme=dark"/>
    <img alt="Star history" src="https://api.star-history.com/svg?repos=AbdulWajid768/inmailer&type=Date"/>
  </picture>
</a>

<br/><br/>

**[Abdul Wajid](https://github.com/AbdulWajid768)** · [abdul45.wajid@gmail.com](mailto:abdul45.wajid@gmail.com)

[![GitHub](https://img.shields.io/badge/@AbdulWajid768-181717?style=flat&logo=github)](https://github.com/AbdulWajid768)


<sub>Style in the lab · Render in the inbox.</sub>

</div>
