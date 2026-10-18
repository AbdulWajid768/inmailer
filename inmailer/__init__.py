"""inmailer: email utilities, including CSS inlining for HTML emails."""

from .core import inline_css, inline_css_file, is_pseudo_selector

__version__ = "0.2.0"

__all__ = ["inline_css", "inline_css_file", "is_pseudo_selector", "__version__"]
