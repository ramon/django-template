from typing import Any

from django import template
from django.forms import BoundField

register = template.Library()

_KNOWN_COLORS = ("danger", "primary", "secondary", "success", "warning")
_WIDGET_TYPES = {"Textarea": "textarea", "RadioSelect": "radio"}


@register.simple_tag
def button_variant(tags: list[str] | None) -> str:
    """Resolve a `<c-ui.button variant>` from an allauth element's `attrs.tags`.

    Args:
        tags: The parsed `attrs.tags` list of an allauth `{% element %}` (e.g.
            `["prominent", "login", "outline", "primary"]`), or `None`.

    Returns:
        `"outline"` (also the default for untagged buttons — most allauth
        buttons are secondary actions like "edit"/"remove"/"activate", not
        the page's one primary call to action), `"link"`, or `"prominent"`.
        `outline`/`link` are checked before `prominent` because allauth tags
        both independently — `"prominent,login,outline,primary"` (the
        passkey/code alternatives on the login page) carries both `prominent`
        (big, full-width) and `outline` (not filled); the visual style tag
        wins over `prominent` alone.
    """
    if tags:
        if "outline" in tags:
            return "outline"
        if "link" in tags:
            return "link"
        if "prominent" in tags:
            return "prominent"
    return "outline"


@register.simple_tag
def button_color(tags: list[str] | None) -> str:
    """Resolve a `<c-ui.button color>` from an allauth element's `attrs.tags`.

    Args:
        tags: The parsed `attrs.tags` list of an allauth `{% element %}`.

    Returns:
        `"danger"`, `"secondary"`, or `"primary"` (default).
    """
    if tags and "danger" in tags:
        return "danger"
    if tags and "secondary" in tags:
        return "secondary"
    return "primary"


@register.filter
def tag_color(tags: list[str] | None) -> str:
    """Pick the first `<c-ui.badge>`/`<c-ui.alert>` color found in `attrs.tags`.

    Args:
        tags: The parsed `attrs.tags` list of an allauth `{% element %}`.

    Returns:
        The first tag matching a known color name, or `"neutral"` if none does.
    """
    if tags:
        for color in _KNOWN_COLORS:
            if color in tags:
                return color
    return "neutral"


@register.filter
def without_tags(attrs: dict[str, Any]) -> dict[str, Any]:
    """Strip the `tags` key from an allauth element's `attrs` dict.

    `attrs.tags` is a Python list, not an HTML-attribute-safe value — merging
    it straight into a `<c-ui.*>` component via `:attrs="attrs"` would render
    as a bogus `tags="['a', 'b']"` attribute on the underlying tag.

    Args:
        attrs: The `attrs` dict of an allauth `{% element %}`.

    Returns:
        A shallow copy of `attrs` without the `tags` key.
    """
    return {key: value for key, value in attrs.items() if key != "tags"}


def _field_type(bound_field: BoundField) -> str:
    widget = bound_field.field.widget
    widget_name = widget.__class__.__name__
    if widget_name in _WIDGET_TYPES:
        return _WIDGET_TYPES[widget_name]
    input_type = getattr(widget, "input_type", None)
    return input_type if input_type else "text"


@register.simple_tag
def field_hide_label(bound_field: BoundField, unlabeled: bool) -> bool:
    """Decide whether a field's `<label>` should be visually hidden.

    Args:
        bound_field: A `BoundField` from the form being rendered.
        unlabeled: The allauth `{% element fields unlabeled=True %}` flag.

    Returns:
        `False` for checkbox/radio fields even when `unlabeled` is set — a
        checkbox has no placeholder to fall back on, unlike a text input, so
        its label always stays visible. `unlabeled` otherwise.
    """
    if not unlabeled:
        return False
    return _field_type(bound_field) not in ("checkbox", "radio")


@register.filter
def field_attrs(bound_field: BoundField) -> dict[str, Any]:
    """Build the `<c-ui.field :attrs>` dict for a form field.

    Used by `allauth/elements/fields.html` to render each `BoundField` of a
    form. django-cotton's tag compiler doesn't support `{% if %}` inside a
    component's attribute list, so the per-field attribute logic (which ones
    apply depends on the widget type) lives here instead of in the template.

    Args:
        bound_field: A `BoundField` from the form being rendered.

    Returns:
        A dict ready for `<c-ui.field :attrs="bound_field|field_attrs">`.
    """
    widget_type = _field_type(bound_field)
    widget_attrs = bound_field.field.widget.attrs
    attrs: dict[str, Any] = {
        "type": widget_type,
        "id": bound_field.id_for_label,
        "name": bound_field.html_name,
        "errors": bound_field.errors,
    }
    if bound_field.field.required:
        attrs["required"] = True
    if bound_field.field.disabled:
        attrs["disabled"] = True
    if widget_type == "checkbox":
        if bound_field.value():
            attrs["checked"] = True
    elif bound_field.value() not in (None, ""):
        attrs["value"] = bound_field.value()
    if widget_attrs.get("placeholder"):
        attrs["placeholder"] = widget_attrs["placeholder"]
    if widget_attrs.get("autocomplete"):
        attrs["autocomplete"] = widget_attrs["autocomplete"]
    if widget_attrs.get("rows"):
        attrs["rows"] = widget_attrs["rows"]
    return attrs
