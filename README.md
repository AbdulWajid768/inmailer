# Inmailer

Pymailer is a Python package that provides email utilities, including CSS inlining for HTML emails.

## Features
- Convert in-file CSS (inside `<style>` tags) into inline styles
- Retain non-inlineable styles (e.g., `@media`, `:hover`) in `<style>`
- Maintain HTML structure while applying styles efficiently

## Installation
```sh
pip install inmailer
```

## Usage

```python
from inmailer import inline_css

html_content = """<html><head><style>h1 { color: red; }</style></head><body><h1>Hello</h1></body></html>"""
processed_html = inline_css(html_content)
print(processed_html)
```

## Contributing
Contributions are welcome! 

To contribute:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.
