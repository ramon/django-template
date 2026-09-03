import pytest
from django.templatetags.static import static

from apps.core.templatetags import vite


def test_get_chunk_raises_a_helpful_key_error_for_an_unknown_entry():
    with pytest.raises(KeyError, match="does not exist in the Vite manifest"):
        vite._get_chunk("frontend/entries/does-not-exist.js")


def test_vite_asset_combines_css_and_js():
    """DEBUG=False in `config.settings.test`, so this resolves against the manifest
    -- either the real build's, or the `vite_manifest_stub` from the root conftest
    when none exists. Either way the entry's chunk has a hashed filename, so this
    checks structure, not a literal path."""
    chunk = vite._get_chunk("frontend/entries/app.js")
    js_src = static(f"dist/{chunk['file']}")

    html = vite.vite_asset("frontend/entries/app.js")

    assert f'src="{js_src}"' in html
    for css_file in chunk.get("css", []):
        css_href = static(f"dist/{css_file}")
        assert f'href="{css_href}"' in html
