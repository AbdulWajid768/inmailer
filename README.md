<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,40:00d4aa,100:16213e&height=200&section=header&text=INMAILER&fontSize=52&fontColor=ffffff&animation=twinkling&desc=CSS+%E2%86%92+inline+%7C+inbox-safe+HTML&descSize=16&descAlignY=72&descAlign=62"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=17&duration=2600&pause=800&color=00D4AA&center=true&vCenter=true&multiline=true&repeat=true&width=640&height=88&lines=Inline+what+Gmail+will+keep;Preserve+%40media+%2B+%3Ahover;One+function%2C+predictable+output;Built+for+newsletters+%26+transactional" alt="Typing animation"/>
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

<img src="https://github-readme-stats.vercel.app/api/pin/?username=AbdulWajid768&repo=inmailer&theme=radical&hide_border=true&bg_color=0d0221&title_color=00d4aa&icon_color=ff006e&text_color=e0e0e0&border_radius=12" width="48%"/>
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=AbdulWajid768&theme=radical&hide_border=true&bg_color=0d0221&title_color=00d4aa&text_color=e0e0e0&layout=compact&border_radius=12" width="48%"/>

<br/><br/>

[📦 Install](#-install) · [⚡ Usage](#-usage) · [🔬 Engine](#-engine)

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=4,5,6&height=2&section=footer" width="100%"/>

</div>

---

## ◈ Transmission

Email clients **amputate** your `<style>` blocks. **Inmailer** rewrites HTML for the inbox era: parse document CSS, **inline** what survives, **rehydrate** `@media`, `@font-face`, and pseudo-rules into a single `<style>` in `<head>`.

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

```bash
git clone https://github.com/AbdulWajid768/inmailer.git
cd inmailer && pip install -e .
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
      h1 { color: #00d4aa; font-size: 24px; }
      a:hover { text-decoration: underline; }
      @media (max-width: 600px) { .wrap { padding: 8px; } }
    </style>
  </head>
  <body><h1>Hello, inbox</h1></body>
</html>
"""

print(inline_css(html_content))
```

---

## ◈ Engine

| Capability | Status |
| --- | --- |
| Inline element/class rules | ✓ |
| Preserve `@media` | ✓ |
| Preserve `:hover` / pseudo | ✓ |
| `!important` merge logic | ✓ |
| Malformed CSS → skip gracefully | ✓ |

---

## ◈ Contributing

Fork → branch → PR. Keep changes surgical in `inmailer/core.py`.

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

<img src="https://komarev.com/ghpvc/?username=AbdulWajid768-inmailer&label=NEURAL%20VIEWS&color=ff006e&style=for-the-badge" alt="views"/>

<sub>Style in the lab · Render in the inbox.</sub>

</div>
