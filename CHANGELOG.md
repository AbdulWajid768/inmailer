# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-10-18

### Added
- **Specificity-aware cascade.** `inline_css` now applies CSS rules following the
  real cascade — more specific selectors and `!important` declarations win,
  instead of relying on source order.
- **Existing inline styles are respected** as the highest-priority author styles
  and merged with (rather than overwritten by) styles from `<style>` tags.
- `extra_css` parameter to inline CSS supplied as a string (e.g. from a separate
  stylesheet file).
- `remove_classes` option to strip `class` attributes after inlining.
- `keep_style_tags` option to also retain the original CSS in a `<style>` tag.
- `pretty_print` option for compact output.
- `inline_css_file()` convenience helper for reading/writing files.
- `inmailer` command-line interface (reads a file or stdin, writes a file or
  stdout) with `--extra-css`, `--remove-classes`, `--keep-style-tags`,
  `--compact`, and `--version`.
- `__version__` attribute and a `py.typed` marker (PEP 561) so type checkers pick
  up the bundled type hints.

### Changed
- Packaging migrated from `setup.py` to `pyproject.toml` (PEP 621).
- Minimum supported Python raised to **3.8**; tested through Python **3.13**, with
  classifiers for 3.8–3.13.
- Dependency floors pinned (`lxml>=4.6`, `cssutils>=2.3`, `cssselect>=1.1`).
- `cssutils` warning noise is silenced by default (re-enable with
  `cssutils.log.setLevel(logging.WARNING)`).

### Fixed
- Malformed or uncompilable selectors no longer crash inlining; they fall back to
  a retained `<style>` tag.

## [0.1.4]
- Initial published releases: basic `<style>` to inline-CSS conversion.
