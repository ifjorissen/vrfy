from django.utils.html import format_html
from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.filters import VisibleWhitespaceFilter


def python_prettify(code, style):
    lexer = PythonLexer()
    lexer.add_filter(VisibleWhitespaceFilter(spaces="&nbsp"))
    pretty_code = highlight(
        code, lexer, HtmlFormatter(
            linenos=style, linenostart=0))
    # print(pretty_code)
    return format_html('{}', mark_safe(pretty_code))
    # return u'{}'.format(pretty_code)
