import re

from inmailer import inline_css, inline_css_file, is_pseudo_selector


def style_of(html_out, tag):
    """Return the style attribute value of the first matching tag in output."""
    match = re.search(rf"<{tag}\b[^>]*\bstyle=\"([^\"]*)\"", html_out)
    return match.group(1) if match else None


def test_is_pseudo_selector_detects_pseudo():
    assert is_pseudo_selector("a:hover") == [":hover"]
    assert is_pseudo_selector("p::first-line") == ["::first-line"]
    assert is_pseudo_selector("div > p") == []


def test_basic_inlining():
    html = "<html><head><style>h1 { color: red; }</style></head><body><h1>Hi</h1></body></html>"
    out = inline_css(html)
    assert "color: red" in style_of(out, "h1")
    assert "<style>" not in out  # the inlined rule leaves nothing behind


def test_pseudo_and_media_rules_are_preserved():
    html = (
        "<html><head><style>"
        "h1 { color: red; } a:hover { color: blue; } "
        "@media (max-width:600px){ h1{font-size:12px} }"
        "</style></head><body><h1>Hi</h1><a href='#'>x</a></body></html>"
    )
    out = inline_css(html)
    assert "color: red" in style_of(out, "h1")
    assert ":hover" in out
    assert "@media" in out


def test_specificity_more_specific_wins():
    # The id rule appears first but is more specific, so it must win over the
    # later element rule. A naive in-order inliner would wrongly pick "red".
    html = (
        "<html><head><style>"
        "#main { color: green; } p { color: red; }"
        "</style></head><body><p id='main'>Hi</p></body></html>"
    )
    out = inline_css(html)
    assert "color: green" in style_of(out, "p")
    assert "color: red" not in style_of(out, "p")


def test_important_beats_higher_specificity():
    html = (
        "<html><head><style>"
        "#main { color: green; } p { color: red !important; }"
        "</style></head><body><p id='main'>Hi</p></body></html>"
    )
    out = inline_css(html)
    assert "color: red" in style_of(out, "p")


def test_existing_inline_style_is_preserved():
    html = (
        "<html><head><style>p { color: red; }</style></head>"
        "<body><p style='color: purple'>Hi</p></body></html>"
    )
    out = inline_css(html)
    assert "color: purple" in style_of(out, "p")


def test_extra_css_is_applied():
    html = "<html><body><h1>Hi</h1></body></html>"
    out = inline_css(html, extra_css="h1 { color: teal; }")
    assert "color: teal" in style_of(out, "h1")


def test_remove_classes():
    html = (
        "<html><head><style>.big { font-size: 20px; }</style></head>"
        "<body><p class='big'>Hi</p></body></html>"
    )
    out = inline_css(html, remove_classes=True)
    assert "font-size: 20px" in style_of(out, "p")
    assert "class=" not in out


def test_keep_style_tags():
    html = "<html><head><style>h1 { color: red; }</style></head><body><h1>Hi</h1></body></html>"
    out = inline_css(html, keep_style_tags=True)
    assert "color: red" in style_of(out, "h1")
    assert "<style>" in out


def test_compact_output_has_no_extra_indentation():
    html = "<html><body><h1>Hi</h1></body></html>"
    out = inline_css(html, extra_css="h1{color:red}", pretty_print=False)
    assert "\n  " not in out


def test_merges_with_existing_inline_without_clobbering():
    html = (
        "<html><head><style>p { color: red; }</style></head>"
        "<body><p style='font-weight: bold'>Hi</p></body></html>"
    )
    out = inline_css(html)
    style = style_of(out, "p")
    assert "font-weight: bold" in style
    assert "color: red" in style


def test_inline_css_file_roundtrip(tmp_path):
    src = tmp_path / "in.html"
    dst = tmp_path / "out.html"
    src.write_text("<html><head><style>h1{color:red}</style></head><body><h1>Hi</h1></body></html>")
    result = inline_css_file(str(src), str(dst))
    assert "color: red" in result
    assert "color: red" in dst.read_text()


def test_link_stylesheet_is_resolved_and_removed(tmp_path):
    (tmp_path / "styles.css").write_text("h1 { color: navy; }")
    html = (
        "<html><head><link rel='stylesheet' href='styles.css'></head>"
        "<body><h1>Hi</h1></body></html>"
    )
    out = inline_css(html, base_path=str(tmp_path))
    assert "color: navy" in style_of(out, "h1")
    assert "<link" not in out  # the resolved link tag is removed


def test_missing_link_is_left_in_place():
    html = (
        "<html><head><link rel='stylesheet' href='nope.css'></head>"
        "<body><h1>Hi</h1></body></html>"
    )
    out = inline_css(html, base_path="/does/not/exist")
    assert "<link" in out  # unresolved link is preserved


def test_remote_link_not_fetched_by_default():
    html = (
        "<html><head><link rel='stylesheet' href='https://example.com/a.css'>"
        "</head><body><h1>Hi</h1></body></html>"
    )
    out = inline_css(html)  # allow_remote defaults to False
    assert "<link" in out


def test_resolve_links_can_be_disabled(tmp_path):
    (tmp_path / "styles.css").write_text("h1 { color: navy; }")
    html = (
        "<html><head><link rel='stylesheet' href='styles.css'></head>"
        "<body><h1>Hi</h1></body></html>"
    )
    out = inline_css(html, base_path=str(tmp_path), resolve_links=False)
    assert style_of(out, "h1") is None
    assert "<link" in out


def test_css_files_param(tmp_path):
    (tmp_path / "a.css").write_text("h1 { color: red; }")
    (tmp_path / "b.css").write_text("h1 { font-size: 20px; }")
    html = "<html><body><h1>Hi</h1></body></html>"
    out = inline_css(html, css_files=["a.css", "b.css"], base_path=str(tmp_path))
    style = style_of(out, "h1")
    assert "color: red" in style
    assert "font-size: 20px" in style


def test_inline_css_file_resolves_relative_link(tmp_path):
    (tmp_path / "styles.css").write_text("p { color: teal; }")
    src = tmp_path / "mail.html"
    src.write_text(
        "<html><head><link rel='stylesheet' href='styles.css'></head>"
        "<body><p>Hi</p></body></html>"
    )
    out = inline_css_file(str(src))  # base_path defaults to the file's dir
    assert "color: teal" in style_of(out, "p")


def test_malformed_selector_does_not_crash():
    html = "<html><head><style>@!! broken { color: red } h1 { color: blue }</style></head><body><h1>Hi</h1></body></html>"
    out = inline_css(html)
    assert "color: blue" in style_of(out, "h1")
