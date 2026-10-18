"""Core CSS inlining utilities for :mod:`inmailer`.

The public entry point is :func:`inline_css`, which moves rules defined in
``<style>`` tags (and any extra CSS you pass in) onto the matching elements as
``style="..."`` attributes. This is the form most email clients understand.
"""

import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Sequence, Tuple

import cssutils
from lxml import html
from lxml.cssselect import CSSSelector

# cssutils is chatty: it logs a WARNING to stderr for every property or value it
# does not recognise (which is common in real-world email CSS). Silence it so the
# library stays quiet by default; callers can raise the level again if they want
# the diagnostics back via ``cssutils.log.setLevel(logging.WARNING)``.
cssutils.log.setLevel(logging.CRITICAL)

__all__ = ["is_pseudo_selector", "inline_css", "inline_css_file"]

# Sort key for styles that already live in a ``style="..."`` attribute. These are
# author inline styles, so they outrank anything coming from a selector
# (specificity ``(1, 0, 0, 0)`` beats every stylesheet selector's ``(0, a, b, c)``).
_INLINE_SPECIFICITY: Tuple[int, int, int, int] = (1, 0, 0, 0)


def is_pseudo_selector(selector: str) -> List[str]:
    """Check whether a CSS selector contains pseudo-classes or pseudo-elements.

    Args:
        selector: The CSS selector string.

    Returns:
        A list of the matched pseudo tokens (e.g. ``[":hover"]``) if any are
        present, otherwise an empty list.
    """
    return re.findall(r':{1,2}[a-zA-Z0-9_-]+', selector)


def _load_css(
    href: str,
    base_path: Optional[str],
    allow_remote: bool,
    encoding: str,
) -> Optional[str]:
    """Read CSS referenced by ``href`` (a stylesheet link or a file path).

    Local paths are resolved relative to ``base_path`` when they are not already
    absolute. Remote (``http``/``https``) URLs are only fetched when
    ``allow_remote`` is ``True``. Returns ``None`` when the CSS cannot be loaded,
    so callers can leave the original ``<link>`` tag in place.
    """
    if not href:
        return None

    parsed = urllib.parse.urlparse(href)

    if parsed.scheme in ("http", "https"):
        if not allow_remote:
            return None
        try:
            with urllib.request.urlopen(href, timeout=10) as response:  # noqa: S310 - opt-in
                return response.read().decode(encoding, errors="replace")
        except Exception:
            return None

    # Local file (no scheme, or an explicit file:// URL).
    path = urllib.parse.unquote(parsed.path) if parsed.scheme == "file" else href
    if base_path and not os.path.isabs(path):
        path = os.path.join(base_path, path)
    try:
        with open(path, "r", encoding=encoding) as handle:
            return handle.read()
    except OSError:
        return None


def _parse_inline_declarations(style_attr: str) -> Dict[str, Tuple[tuple, str]]:
    """Return ``{property_name: (sort_key, value)}`` for an element's ``style``."""
    winners: Dict[str, Tuple[tuple, str]] = {}
    if not style_attr:
        return winners

    declaration = cssutils.parseStyle(style_attr)
    for prop in declaration:
        important = 1 if prop.priority == 'important' else 0
        # order is irrelevant for inline styles (they share one specificity), so
        # use -1 purely as a stable tiebreaker.
        winners[prop.name] = ((important, _INLINE_SPECIFICITY, -1), prop.value)
    return winners


def _collect_rules(css_text: str):
    """Split parsed CSS into inlineable selector entries and leftover rules.

    Returns a tuple ``(inlineable, non_inlineable)`` where ``inlineable`` is a
    list of ``(specificity, order, selector_text, declaration)`` tuples and
    ``non_inlineable`` is the list of rules that must stay inside a ``<style>``
    tag (media queries, font faces, pseudo-class rules, etc.).
    """
    inlineable = []
    non_inlineable = []
    order = 0

    try:
        style_sheet = cssutils.parseString(css_text)
    except Exception:
        return inlineable, non_inlineable

    for rule in style_sheet:
        if rule.type == rule.STYLE_RULE:
            # A rule is kept intact in a <style> tag when any of its selectors
            # rely on pseudo-classes/elements, which cannot be expressed inline.
            if is_pseudo_selector(rule.selectorText):
                non_inlineable.append(rule)
                continue

            for selector in rule.selectorList:
                inlineable.append(
                    (selector.specificity, order, selector.selectorText, rule.style)
                )
                order += 1
        else:
            non_inlineable.append(rule)

    return inlineable, non_inlineable


def inline_css(
    html_content: str,
    extra_css: Optional[str] = None,
    *,
    css_files: Optional[Sequence[str]] = None,
    base_path: Optional[str] = None,
    resolve_links: bool = True,
    allow_remote: bool = False,
    encoding: str = "utf-8",
    remove_classes: bool = False,
    keep_style_tags: bool = False,
    pretty_print: bool = True,
) -> str:
    """Convert ``<style>`` CSS (and optional extra CSS) into inline styles.

    Rules are applied following the CSS cascade: declarations from more specific
    selectors (and ``!important`` declarations) win, and existing inline styles
    on an element are preserved as the highest-priority author styles.

    Non-inlineable CSS (``@media`` queries, ``@font-face``, ``:hover`` and other
    pseudo rules) is re-inserted into a ``<style>`` tag in the document head.

    Args:
        html_content: The HTML document as a string.
        extra_css: Additional CSS (as a string) to inline alongside the
            document's own ``<style>`` tags. Applied last, so it overrides equal
            specificity rules from the document.
        css_files: Paths to external CSS files to read and inline. Relative paths
            are resolved against ``base_path``.
        base_path: Directory used to resolve relative ``<link>`` hrefs and
            ``css_files`` paths.
        resolve_links: When ``True`` (default), ``<link rel="stylesheet">`` tags
            are read and inlined. Links that cannot be loaded are left in place.
        allow_remote: When ``True``, ``http``/``https`` stylesheet links are
            fetched over the network. Off by default for safety.
        encoding: Text encoding used when reading linked/external CSS files.
        remove_classes: When ``True``, strip ``class`` attributes after inlining
            to shrink the output (ids are kept so anchors keep working).
        keep_style_tags: When ``True``, also retain the original CSS in a
            ``<style>`` tag, for clients that support embedded styles.
        pretty_print: When ``True`` (default), return indented HTML. Set to
            ``False`` for compact output, which some email clients prefer.

    Returns:
        The modified HTML with inline styles applied where possible.
    """
    document = html.fromstring(html_content)

    # Collect CSS from <style> tags and <link rel="stylesheet"> tags in document
    # order so the cascade matches how a browser reads the document. Nodes are
    # gathered first, then consumed, to avoid mutating the tree while iterating.
    collected_css: List[str] = []
    consumed_nodes = []

    for node in list(document.iter("style", "link")):
        if node.tag == "style":
            if node.text:
                collected_css.append(node.text)
            consumed_nodes.append(node)
        elif resolve_links and node.tag == "link":
            rel = (node.get("rel") or "").lower().split()
            if "stylesheet" in rel:
                css = _load_css(node.get("href"), base_path, allow_remote, encoding)
                if css is not None:
                    collected_css.append(css)
                    consumed_nodes.append(node)

    for path in css_files or []:
        resolved = path
        if base_path and not os.path.isabs(path):
            resolved = os.path.join(base_path, path)
        try:
            with open(resolved, "r", encoding=encoding) as handle:
                collected_css.append(handle.read())
        except OSError:
            continue

    if extra_css:
        collected_css.append(extra_css)
    original_css = "\n".join(collected_css)

    for node in consumed_nodes:
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)

    inlineable, non_inlineable_rules = _collect_rules(original_css)

    # Apply from lowest to highest priority so that higher-priority declarations
    # overwrite lower-priority ones. Priority = (!important, specificity, order).
    inlineable.sort(key=lambda entry: (entry[0], entry[1]))

    # Seed each element with the styles it already carries inline.
    winners: Dict[object, Dict[str, Tuple[tuple, str]]] = {}

    for specificity, order, selector_text, declaration in inlineable:
        try:
            selector = CSSSelector(selector_text)
        except Exception:
            # cssselect raises a variety of errors on selectors lxml cannot
            # compile; keep the rule in a <style> tag rather than dropping it.
            parent_rule = getattr(declaration, 'parentRule', None)
            if parent_rule is not None:
                non_inlineable_rules.append(parent_rule)
            continue

        for element in selector(document):
            element_styles = winners.get(element)
            if element_styles is None:
                element_styles = _parse_inline_declarations(element.get('style', ''))
                winners[element] = element_styles

            for prop in declaration:
                important = 1 if prop.priority == 'important' else 0
                sort_key = (important, specificity, order)
                existing = element_styles.get(prop.name)
                if existing is None or sort_key >= existing[0]:
                    element_styles[prop.name] = (sort_key, prop.value)

    for element, element_styles in winners.items():
        inline_style = '; '.join(
            f"{name}: {value}" for name, (_, value) in element_styles.items()
        )
        if inline_style:
            element.set('style', inline_style)

    if remove_classes:
        for element in document.xpath('//*[@class]'):
            del element.attrib['class']

    _reinsert_style_tags(document, non_inlineable_rules, original_css, keep_style_tags)

    return html.tostring(document, encoding='unicode', pretty_print=pretty_print)


def _reinsert_style_tags(document, non_inlineable_rules, original_css, keep_style_tags):
    """Put leftover (and optionally original) CSS back into a ``<style>`` tag."""
    css_parts: List[str] = []

    if keep_style_tags and original_css.strip():
        css_parts.append(original_css.strip())
    else:
        # Deduplicate rules while preserving order (a rule may be appended twice
        # if its selector also failed to compile).
        seen = set()
        for rule in non_inlineable_rules:
            text = getattr(rule, 'cssText', None)
            if text and text not in seen:
                seen.add(text)
                css_parts.append(text)

    if not css_parts:
        return

    new_style = html.Element('style')
    new_style.text = "\n".join(css_parts)

    head = document.find('head')
    if head is None:
        head = html.Element('head')
        document.insert(0, head)
    head.append(new_style)


def inline_css_file(
    input_path: str,
    output_path: Optional[str] = None,
    *,
    encoding: str = "utf-8",
    **kwargs,
) -> str:
    """Inline the CSS of an HTML file and optionally write the result to disk.

    Relative ``<link>`` hrefs and ``css_files`` are resolved against the input
    file's directory unless a ``base_path`` is passed explicitly.

    Args:
        input_path: Path to the source HTML file.
        output_path: If given, the inlined HTML is written here.
        encoding: Text encoding used to read and write the files.
        **kwargs: Forwarded to :func:`inline_css` (e.g. ``remove_classes``).

    Returns:
        The inlined HTML as a string.
    """
    kwargs.setdefault("base_path", os.path.dirname(os.path.abspath(input_path)))
    kwargs.setdefault("encoding", encoding)
    with open(input_path, "r", encoding=encoding) as handle:
        result = inline_css(handle.read(), **kwargs)

    if output_path:
        with open(output_path, "w", encoding=encoding) as handle:
            handle.write(result)

    return result
