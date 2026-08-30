"""Contract tests for the `<c-ui.*>` component kit.

Each test renders the real template and asserts the prop -> markup contract and that
`{{ attrs }}` passthrough lands on the right element. Text is never asserted (the UI is
translated); assertions are about structure, classes and attributes.
"""

from apps.ui.tests.integration.cotton import opening_tag, render


class TestButton:
    def test_renders_button_by_default(self):
        tag = opening_tag(render("<c-ui.button>Go</c-ui.button>"), r"<button\b[^>]*>")
        assert 'type="button"' in tag

    def test_renders_anchor_when_href_is_set(self):
        html = render('<c-ui.button href="/next">Go</c-ui.button>')
        assert opening_tag(html, r"<a\b[^>]*>")
        assert 'href="/next"' in opening_tag(html, r"<a\b[^>]*>")
        assert not opening_tag(html, r"<button\b[^>]*>")

    def test_variant_and_color_select_style_classes(self):
        tag = opening_tag(
            render('<c-ui.button variant="outline" color="danger">Go</c-ui.button>'),
            r"<button\b[^>]*>",
        )
        assert "border-error" in tag
        assert "text-error" in tag

    def test_forwards_native_attrs_to_the_element(self):
        tag = opening_tag(
            render('<c-ui.button data-role="cta" hx-get="/x" disabled>Go</c-ui.button>'),
            r"<button\b[^>]*>",
        )
        assert 'data-role="cta"' in tag
        assert 'hx-get="/x"' in tag
        assert "disabled" in tag

    def test_caller_class_is_appended_once(self):
        tag = opening_tag(
            render('<c-ui.button class="w-full">Go</c-ui.button>'), r"<button\b[^>]*>"
        )
        assert "w-full" in tag
        assert tag.count('class="') == 1


class TestButtonGroup:
    def test_horizontal_by_default(self):
        tag = opening_tag(render("<c-ui.button_group>x</c-ui.button_group>"), r"<div\b[^>]*>")
        assert "flex-wrap" in tag
        assert "flex-col" not in tag

    def test_vertical_stacks_in_a_column(self):
        tag = opening_tag(
            render("<c-ui.button_group vertical>x</c-ui.button_group>"), r"<div\b[^>]*>"
        )
        assert "flex-col" in tag


class TestBadge:
    def test_color_selects_token_classes(self):
        tag = opening_tag(render('<c-ui.badge color="danger">x</c-ui.badge>'), r"<span\b[^>]*>")
        assert "bg-error-container" in tag

    def test_unknown_defaults_to_neutral(self):
        tag = opening_tag(render("<c-ui.badge>x</c-ui.badge>"), r"<span\b[^>]*>")
        assert "bg-surface-container-high" in tag

    def test_forwards_attrs_and_class(self):
        tag = opening_tag(
            render('<c-ui.badge class="ml-2" data-x="1">x</c-ui.badge>'), r"<span\b[^>]*>"
        )
        assert "ml-2" in tag
        assert 'data-x="1"' in tag
        assert tag.count('class="') == 1


class TestAlert:
    def test_has_alert_role(self):
        assert opening_tag(render("<c-ui.alert>x</c-ui.alert>"), r'<div role="alert"[^>]*>')

    def test_severity_selects_container_and_dot_classes(self):
        html = render('<c-ui.alert severity="error">x</c-ui.alert>')
        assert "bg-error-container" in opening_tag(html, r'<div role="alert"[^>]*>')
        assert "bg-error" in opening_tag(html, r"<span [^>]*>")


class TestField:
    def test_renders_label_bound_to_input_id(self):
        html = render('<c-ui.field label="Email" id="id_email" name="email" />')
        assert 'for="id_email"' in opening_tag(html, r"<label\b[^>]*>")
        assert 'id="id_email"' in opening_tag(html, r"<input\b[^>]*>")

    def test_textarea_type_renders_a_textarea(self):
        html = render('<c-ui.field type="textarea" name="bio" />')
        assert opening_tag(html, r"<textarea\b[^>]*>")

    def test_checkbox_type_renders_a_checkbox_input(self):
        html = render('<c-ui.field type="checkbox" name="agree" />')
        assert 'type="checkbox"' in opening_tag(html, r"<input\b[^>]*>")

    def test_attrs_land_on_the_control_not_the_wrapper(self):
        html = render('<c-ui.field name="q" hx-get="/s" data-role="search" />')
        control = opening_tag(html, r"<input\b[^>]*>")
        assert 'hx-get="/s"' in control
        assert 'data-role="search"' in control

    def test_hide_label_keeps_the_label_in_the_dom(self):
        html = render('<c-ui.field label="Query" name="q" hide_label />')
        label = opening_tag(html, r"<label\b[^>]*>")
        assert label
        assert "sr-only" in label

    def test_errors_render_as_a_list(self):
        html = render("<c-ui.field name=\"q\" :errors=\"['too short', 'required']\" />")
        assert "too short" in html
        assert "required" in html


class TestForm:
    def test_method_and_action(self):
        tag = opening_tag(
            render('<c-ui.form method="get" action="/search">x</c-ui.form>'),
            r"<form\b[^>]*>",
        )
        assert 'method="get"' in tag
        assert 'action="/search"' in tag

    def test_actions_slot_renders_a_trailing_band(self):
        html = render(
            '<c-ui.form><c-slot name="actions"><button>Save</button></c-slot>body</c-ui.form>'
        )
        assert "justify-end" in html


class TestPanel:
    def test_title_renders_a_heading(self):
        html = render('<c-ui.panel title="Settings">body</c-ui.panel>')
        assert opening_tag(html, r"<h2\b[^>]*>")
        assert "Settings" in html

    def test_no_heading_without_title(self):
        html = render("<c-ui.panel>body</c-ui.panel>")
        assert not opening_tag(html, r"<h2\b[^>]*>")

    def test_forwards_attrs_and_class(self):
        tag = opening_tag(
            render('<c-ui.panel class="mt-4" data-x="1">body</c-ui.panel>'),
            r"<section\b[^>]*>",
        )
        assert "mt-4" in tag
        assert 'data-x="1"' in tag
        assert tag.count('class="') == 1


class TestTypography:
    def test_headings_and_paragraph_forward_class_and_attrs(self):
        for tag_name, comp in [("h1", "h1"), ("h2", "h2"), ("p", "p")]:
            el = opening_tag(
                render(f'<c-ui.{comp} class="mb-2" id="x">t</c-ui.{comp}>'),
                rf"<{tag_name}\b[^>]*>",
            )
            assert "mb-2" in el
            assert 'id="x"' in el
            assert el.count('class="') == 1

    def test_hr_forwards_class(self):
        assert "mt-8" in opening_tag(render('<c-ui.hr class="mt-8" />'), r"<hr\b[^>]*>")


class TestTable:
    def test_table_wraps_in_a_horizontal_scroll_container(self):
        html = render("<c-ui.table><tbody></tbody></c-ui.table>")
        assert "overflow-x-auto" in html

    def test_td_align_right(self):
        tag = opening_tag(render('<c-ui.td align="right">v</c-ui.td>'), r"<td\b[^>]*>")
        assert "text-right" in tag

    def test_td_default_is_not_right_aligned(self):
        tag = opening_tag(render("<c-ui.td>v</c-ui.td>"), r"<td\b[^>]*>")
        assert "text-right" not in tag
