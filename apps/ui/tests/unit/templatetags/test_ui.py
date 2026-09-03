"""Unit tests for the pure functions behind the `<c-ui.*>` template tags/filters.

Past the `@register.*` decorator these are plain functions, called directly here --
no template rendering needed. `apps/ui/tests/integration/test_components.py` covers
the templates that some of them (`field_attrs`, `field_hide_label`) feed into.
"""

from django import forms

from apps.ui.templatetags import ui


class TestButtonVariant:
    def test_no_tags_falls_back_to_outline(self):
        assert ui.button_variant(None) == "outline"

    def test_unmatched_tags_fall_back_to_outline(self):
        assert ui.button_variant(["login"]) == "outline"

    def test_outline_tag_wins(self):
        assert ui.button_variant(["prominent", "outline"]) == "outline"

    def test_link_tag_is_picked_when_outline_is_absent(self):
        assert ui.button_variant(["link", "prominent"]) == "link"

    def test_prominent_tag_alone(self):
        assert ui.button_variant(["prominent"]) == "prominent"


class TestButtonColor:
    def test_no_tags_falls_back_to_primary(self):
        assert ui.button_color(None) == "primary"

    def test_danger_tag(self):
        assert ui.button_color(["danger"]) == "danger"

    def test_secondary_tag(self):
        assert ui.button_color(["secondary"]) == "secondary"


class TestTagColor:
    def test_no_tags_is_neutral(self):
        assert ui.tag_color(None) == "neutral"

    def test_unmatched_tags_are_neutral(self):
        assert ui.tag_color(["unknown"]) == "neutral"

    def test_first_known_color_wins(self):
        assert ui.tag_color(["warning", "danger"]) == "danger"


class TestWithoutTags:
    def test_strips_only_tags(self):
        assert ui.without_tags({"tags": ["a"], "id": "x"}) == {"id": "x"}


class TestWithoutTagsAndForm:
    def test_strips_tags_and_form(self):
        attrs = {"tags": ["a"], "form": object(), "id": "x"}
        assert ui.without_tags_and_form(attrs) == {"id": "x"}


class _Form(forms.Form):
    text = forms.CharField()
    optional_text = forms.CharField(required=False)
    disabled_text = forms.CharField(disabled=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    choice = forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect)
    accepts = forms.BooleanField(required=False)
    hinted = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "ex: Ada", "autocomplete": "name"})
    )


class TestFieldType:
    def test_maps_textarea_to_its_own_type(self):
        assert ui._field_type(_Form()["comment"]) == "textarea"

    def test_maps_radio_select_to_its_own_type(self):
        assert ui._field_type(_Form()["choice"]) == "radio"

    def test_falls_back_to_the_widget_input_type(self):
        assert ui._field_type(_Form()["text"]) == "text"


class TestFieldHideLabel:
    def test_checkbox_keeps_its_label_even_when_unlabeled(self):
        assert ui.field_hide_label(_Form()["accepts"], unlabeled=True) is False

    def test_text_field_hides_its_label_when_unlabeled(self):
        assert ui.field_hide_label(_Form()["text"], unlabeled=True) is True

    def test_label_stays_visible_when_not_unlabeled(self):
        assert ui.field_hide_label(_Form()["text"], unlabeled=False) is False


class TestFieldAttrs:
    def test_required_field_gets_the_required_attr(self):
        assert ui.field_attrs(_Form()["text"])["required"] is True

    def test_optional_field_has_no_required_attr(self):
        assert "required" not in ui.field_attrs(_Form()["optional_text"])

    def test_disabled_field_gets_the_disabled_attr(self):
        assert ui.field_attrs(_Form()["disabled_text"])["disabled"] is True

    def test_checked_checkbox_gets_the_checked_attr(self):
        form = _Form(data={"accepts": "on"})
        assert ui.field_attrs(form["accepts"])["checked"] is True

    def test_unchecked_checkbox_has_no_checked_attr(self):
        form = _Form(data={})
        assert "checked" not in ui.field_attrs(form["accepts"])

    def test_non_checkbox_field_gets_its_value(self):
        form = _Form(data={"text": "Ada"})
        assert ui.field_attrs(form["text"])["value"] == "Ada"

    def test_placeholder_and_autocomplete_pass_through(self):
        attrs = ui.field_attrs(_Form()["hinted"])
        assert attrs["placeholder"] == "ex: Ada"
        assert attrs["autocomplete"] == "name"

    def test_rows_passes_through_for_textarea(self):
        assert ui.field_attrs(_Form()["comment"])["rows"] == 4
