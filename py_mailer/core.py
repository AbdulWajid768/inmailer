import re
import cssutils
from lxml import html
from lxml.cssselect import CSSSelector, ExpressionError


def is_pseudo_selector(selector: str) -> list:
    """
    Checks if a CSS selector contains pseudo-selectors.

    Args:
        selector (str): The CSS selector string.

    Returns:
        list: A list of matched pseudo-selectors if found, otherwise an empty list.
    """
    return re.findall(r':{1,2}[a-zA-Z0-9_-]+', selector)


def inline_css(html_content: str) -> str:
    """
    Converts in-file CSS (inside <style> tags) to inline CSS where possible.

    Non-inlineable CSS (e.g., media queries, @font-face, or pseudo-classes like :hover)
    is re-inserted into a <style> tag.

    Args:
        html_content (str): The HTML content as a string.

    Returns:
        str: The modified HTML with inline styles applied where possible.
    """
    document = html.fromstring(html_content)
    style_tags = document.xpath('//style')

    inlineable_rules = []
    non_inlineable_rules = []

    for style_tag in style_tags:
        try:
            style_sheet = cssutils.parseString(style_tag.text)
        except Exception:
            continue

        for rule in style_sheet:
            if rule.type == rule.STYLE_RULE:
                if is_pseudo_selector(rule.selectorText):
                    non_inlineable_rules.append(rule)
                else:
                    inlineable_rules.append(rule)
            else:
                non_inlineable_rules.append(rule)

        style_tag.getparent().remove(style_tag)

    for rule in inlineable_rules:
        try:
            selector = CSSSelector(rule.selectorText)
        except ExpressionError:
            non_inlineable_rules.append(rule)
            continue

        elements = selector(document)
        for element in elements:
            current_styles = element.get('style', '')
            style_declaration = cssutils.parseStyle(current_styles)
            style_map = {prop.name: prop.value for prop in style_declaration}

            for prop in rule.style:
                if prop.name not in style_map or prop.priority == 'important':
                    style_map[prop.name] = prop.value

            inline_style = '; '.join(f"{name}: {value}" for name, value in style_map.items())
            element.set('style', inline_style)

    if non_inlineable_rules:
        new_style = html.Element('style')
        css_texts = [rule.cssText for rule in non_inlineable_rules if hasattr(rule, 'cssText')]
        new_style.text = "\n".join(css_texts)

        head = document.find('head')
        if head is None:
            head = html.Element('head')
            document.insert(0, head)
        head.append(new_style)

    return html.tostring(document, encoding='unicode', pretty_print=True)