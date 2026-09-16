import json
from functools import lru_cache
from typing import Any

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
MULTI_ENTRY_MANIFEST: dict[str, dict[str, Any]] = {
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


@pytest.fixture
def collected_multi_entry(collect_static):
    """The files of `MULTI_ENTRY_MANIFEST`, collected by the production storage."""
    files = {
        f"dist/{file}": "/* built by vite */"
        for chunk in MULTI_ENTRY_MANIFEST.values()
        for file in [chunk["file"], *chunk.get("css", [])]
    }
    return collect_static(files)


@pytest.mark.usefixtures("multi_entry_manifest", "collected_multi_entry")
def test_vite_js_requests_chunks_by_the_name_in_the_vite_manifest():
    """The chunks import each other by the name Vite wrote. A preload or entry URL
    under any other name is a second module: the browser downloads it twice."""
    html = vite.vite_js("frontend/entries/admin.js")

    assert '<script type="module" src="/static/dist/assets/admin-b2.js"></script>' in html
    for file in ("assets/shared-abc.js", "assets/widgets-def.js"):
        assert f'<link rel="modulepreload" href="/static/dist/{file}" />' in html


@pytest.mark.usefixtures("multi_entry_manifest", "collected_multi_entry")
def test_vite_css_requests_files_by_the_name_in_the_vite_manifest():
    html = vite.vite_css("frontend/entries/admin.js")

    assert 'href="/static/dist/assets/shared-abc.css"' in html


@pytest.mark.usefixtures("multi_entry_manifest")
def test_vite_js_keeps_vite_names_when_static_url_is_a_cdn(collect_static, settings):
    settings.STATIC_URL = "https://cdn.example.com/static/"
    collect_static({"dist/assets/app-a1.js": "", "dist/assets/shared-abc.js": ""})

    html = vite.vite_js("frontend/entries/app.js")

    assert 'src="https://cdn.example.com/static/dist/assets/app-a1.js"' in html
    assert 'href="https://cdn.example.com/static/dist/assets/shared-abc.js"' in html


REMOTE_MANIFEST = {
    "frontend/entries/app.js": {"file": "assets/app-remote.js", "src": "frontend/entries/app.js"},
}
remote_calls: list[None] = []


def load_remote_manifest():
    """Stands in for a loader that fetches the manifest from a bucket or a CDN."""
    remote_calls.append(None)
    return REMOTE_MANIFEST


@pytest.fixture
def configured_manifest(monkeypatch):
    """
    Loads the manifest the way production does, from the configured loader.

    The session stub in the root conftest replaces `_load_manifest` when there is
    no build, and the real one caches across tests; a fresh cache over the
    uncached reader sidesteps both.
    """
    remote_calls.clear()
    monkeypatch.setattr(vite, "_load_manifest", lru_cache(maxsize=1)(vite._read_manifest))


@pytest.mark.usefixtures("configured_manifest")
def test_default_loader_reads_the_file_at_vite_manifest_path(settings, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(REMOTE_MANIFEST), encoding="utf-8")
    settings.VITE_MANIFEST_PATH = manifest

    html = vite.vite_js("frontend/entries/app.js")

    assert f'src="{static("dist/assets/app-remote.js")}"' in html


@pytest.mark.usefixtures("configured_manifest")
def test_vite_manifest_loader_replaces_the_file(settings, tmp_path):
    settings.VITE_MANIFEST_PATH = tmp_path / "does-not-exist.json"
    settings.VITE_MANIFEST_LOADER = f"{__name__}.load_remote_manifest"

    html = vite.vite_js("frontend/entries/app.js")

    assert f'src="{static("dist/assets/app-remote.js")}"' in html


@pytest.mark.usefixtures("configured_manifest")
def test_vite_manifest_loader_runs_once_per_process(settings):
    """A remote loader means a network round trip; it must not happen per render."""
    settings.VITE_MANIFEST_LOADER = f"{__name__}.load_remote_manifest"

    vite.vite_js("frontend/entries/app.js")
    vite.vite_css("frontend/entries/app.js")

    assert len(remote_calls) == 1
