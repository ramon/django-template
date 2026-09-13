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


# Two entrypoints sharing code, the shape Rollup produces as soon as there is more
# than one input: the common module -- and the CSS it imports -- moves to a shared
# chunk, and the manifest lists that CSS there, not on the entries.
MULTI_ENTRY_MANIFEST = {
    "frontend/entries/app.js": {
        "file": "assets/app-a1.js",
        "src": "frontend/entries/app.js",
        "isEntry": True,
        "imports": ["_shared-abc.js"],
        "css": ["assets/app-a1.css"],
    },
    "frontend/entries/admin.js": {
        "file": "assets/admin-b2.js",
        "src": "frontend/entries/admin.js",
        "isEntry": True,
        "imports": ["_shared-abc.js", "_widgets-def.js"],
    },
    "_shared-abc.js": {
        "file": "assets/shared-abc.js",
        "css": ["assets/shared-abc.css"],
    },
    # a second path to the shared chunk, so admin reaches it twice
    "_widgets-def.js": {
        "file": "assets/widgets-def.js",
        "imports": ["_shared-abc.js"],
        "css": ["assets/widgets-def.css"],
    },
    # a cycle between chunks, which Rollup can emit for circular imports
    "frontend/entries/cyclic.js": {
        "file": "assets/cyclic-c3.js",
        "src": "frontend/entries/cyclic.js",
        "isEntry": True,
        "imports": ["_ping-111.js"],
    },
    "_ping-111.js": {
        "file": "assets/ping-111.js",
        "imports": ["_pong-222.js"],
        "css": ["assets/ping-111.css"],
    },
    "_pong-222.js": {
        "file": "assets/pong-222.js",
        "imports": ["_ping-111.js", "frontend/entries/cyclic.js"],
    },
}


@pytest.fixture
def multi_entry_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vite, "_load_manifest", lambda: MULTI_ENTRY_MANIFEST)


def _href(file: str) -> str:
    return f'href="{static(f"dist/{file}")}"'


@pytest.mark.usefixtures("multi_entry_manifest")
@pytest.mark.parametrize("entry", ["frontend/entries/app.js", "frontend/entries/admin.js"])
def test_vite_css_includes_the_css_of_imported_chunks(entry):
    html = vite.vite_css(entry)

    assert f'<link rel="stylesheet" {_href("assets/shared-abc.css")} />' in html


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_css_keeps_the_entry_css():
    html = vite.vite_css("frontend/entries/app.js")

    assert _href("assets/app-a1.css") in html


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_css_follows_imports_recursively_without_repeating_a_chunk():
    html = vite.vite_css("frontend/entries/admin.js")

    assert html.count(_href("assets/shared-abc.css")) == 1
    assert _href("assets/widgets-def.css") in html


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_css_puts_dependency_css_before_the_css_that_depends_on_it():
    """Same order Vite uses in the HTML it builds itself: whoever imports a chunk
    can override its styles."""
    html = vite.vite_css("frontend/entries/admin.js")

    assert html.index(_href("assets/shared-abc.css")) < html.index(_href("assets/widgets-def.css"))


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_css_survives_an_import_cycle():
    html = vite.vite_css("frontend/entries/cyclic.js")

    assert html.count(_href("assets/ping-111.css")) == 1


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_js_preloads_every_imported_chunk_once():
    html = vite.vite_js("frontend/entries/admin.js")

    for file in ("assets/shared-abc.js", "assets/widgets-def.js"):
        assert html.count(f'<link rel="modulepreload" {_href(file)} />') == 1
    assert 'rel="modulepreload" ' + _href("assets/admin-b2.js") not in html


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_asset_emits_all_css_before_the_script():
    html = vite.vite_asset("frontend/entries/admin.js")

    script = html.index("<script")
    assert html.index(_href("assets/shared-abc.css")) < script
    assert html.index(_href("assets/widgets-def.css")) < script


def test_vite_js_uses_the_configured_dev_server_url(settings):
    settings.DEBUG = True
    settings.VITE_DEV_SERVER_URL = "http://127.0.0.1:9123"

    html = vite.vite_js("frontend/entries/app.js")

    assert '<script type="module" src="http://127.0.0.1:9123/@vite/client"></script>' in html
    assert (
        '<script type="module" src="http://127.0.0.1:9123/frontend/entries/app.js"></script>'
        in html
    )
    assert "8001" not in html
