"""Core CSS inlining utilities for :mod:`inmailer`.

The public entry point is :func:`inline_css`, which moves rules defined in
``<style>`` tags (and any extra CSS you pass in) onto the matching elements as
``style="..."`` attributes. This is the form most email clients understand.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

import cssutils
from lxml import html
from lxml.cssselect import CSSSelector, ExpressionError

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
        extra_css: Additional CSS (e.g. loaded from a separate file) to inline
            alongside the document's own ``<style>`` tags.
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
    style_tags = document.xpath('//style')

    collected_css = [tag.text for tag in style_tags if tag.text]
    if extra_css:
        collected_css.append(extra_css)
    original_css = "\n".join(collected_css)

    for style_tag in style_tags:
        parent = style_tag.getparent()
        if parent is not None:
            parent.remove(style_tag)

    inlineable, non_inlineable_rules = _collect_rules(original_css)

    # Apply from lowest to highest priority so that higher-priority declarations
    # overwrite lower-priority ones. Priority = (!important, specificity, order).
    inlineable.sort(key=lambda entry: (entry[0], entry[1]))

    # Seed each element with the styles it already carries inline.
    winners: Dict[object, Dict[str, Tuple[tuple, str]]] = {}

    for specificity, order, selector_text, declaration in inlineable:
        try:
            selector = CSSSelector(selector_text)
        except (ExpressionError, Exception):  # noqa: B014 - cssselect raises varied types
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

    Args:
        input_path: Path to the source HTML file.
        output_path: If given, the inlined HTML is written here.
        encoding: Text encoding used to read and write the files.
        **kwargs: Forwarded to :func:`inline_css` (e.g. ``remove_classes``).

    Returns:
        The inlined HTML as a string.
    """
    with open(input_path, "r", encoding=encoding) as handle:
        result = inline_css(handle.read(), **kwargs)

    if output_path:
        with open(output_path, "w", encoding=encoding) as handle:
            handle.write(result)

    return result
