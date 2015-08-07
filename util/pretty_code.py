from django.utils.html import format_html
from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def python_prettify(code, style):
  pretty_code = highlight(code, PythonLexer(), HtmlFormatter(linenos=style))
  return format_html('{}', mark_safe(pretty_code))