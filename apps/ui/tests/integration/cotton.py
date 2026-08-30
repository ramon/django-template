"""Render kit components against the real templates.

In the mold of django-cotton-ui's own test helper: compile a component-source string
with the cotton compiler, then render it. The real files in
`apps/ui/templates/components/ui/**` are resolved by the cotton loader, so these tests
exercise the shipped templates, not fixtures.
"""

import re

from django.template import Context, Template
from django_cotton.compiler_regex import CottonCompiler


def render(source: str, **context: object) -> str:
    """Compile and render a snippet that uses `<c-ui.*>` components."""
    compiled = CottonCompiler().process(source)
    return Template(compiled).render(Context(context))


def opening_tag(html: str, pattern: str) -> str:
    """First opening tag matching `pattern`, whitespace collapsed, or '' if absent."""
    match = re.search(pattern, re.sub(r"\s+", " ", html))
    return match.group(0) if match else ""
