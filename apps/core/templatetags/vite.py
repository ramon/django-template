import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


def _manifest_path() -> Path:
    """
    Retrieves the path of the Vite manifest file.

    Returns:
        Path: `settings.VITE_MANIFEST_PATH`, by default the manifest `bun run build`
        writes to `static/dist/.vite/`.
    """
    return Path(settings.VITE_MANIFEST_PATH)


def read_manifest_file() -> dict[str, Any]:
    """
    Reads the Vite manifest from `settings.VITE_MANIFEST_PATH`.

    The default `VITE_MANIFEST_LOADER`. A replacement takes no arguments and
    returns the parsed manifest in the same shape.

    Returns:
        dict[str, Any]: The parsed manifest.

    Raises:
        JSONDecodeError: If the file's contents cannot be parsed into a valid JSON object.
        FileNotFoundError: If the manifest file does not exist at the expected location.
    """
    manifest: dict[str, Any] = json.loads(_manifest_path().read_text(encoding="utf-8"))
    return manifest


def _read_manifest() -> dict[str, Any]:
    """
    Loads the manifest with the function named in `settings.VITE_MANIFEST_LOADER`.

    Returns:
        dict[str, Any]: The manifest the loader returns.

    Raises:
        ImportError: If `VITE_MANIFEST_LOADER` is not an importable dotted path.
    """
    loader: Callable[[], dict[str, Any]] = import_string(settings.VITE_MANIFEST_LOADER)
    return loader()


@lru_cache(maxsize=1)
def _load_manifest() -> dict[str, Any]:
    """
    Loads the Vite manifest once per process.

    The manifest only changes with a new build, which comes with a new deploy, and
    a loader that reads from a bucket would otherwise cost a round trip per render.

    Returns:
        dict[str, Any]: The manifest returned by the configured loader.
    """
    return _read_manifest()


def _get_chunk(entry: str) -> dict[str, Any]:
    """
    Resolves an entry in the Vite manifest.

    `entry` is the manifest key, which Vite generates from the input path
    relative to the project root (e.g. "frontend/entries/app.js"). The same
    string serves the dev server, avoiding a parallel mapping between dev and
    production.

    Args:
        entry: The manifest key to look up.

    Returns:
        dict[str, Any]: The manifest entry for `entry`.

    Raises:
        KeyError: If `entry` is not present in the manifest.
    """
    manifest = _load_manifest()

    try:
        chunk: dict[str, Any] = manifest[entry]
        return chunk
    except KeyError:
        available = ", ".join(sorted(manifest)) or "<empty manifest>"
        raise KeyError(
            f"Entry '{entry}' does not exist in the Vite manifest. Available: {available}. "
            f"Run `bun run vite build`."
        ) from None


def _render_dev_css() -> str:
    """
    Generates and returns CSS rules for development purposes.

    This function is intended to dynamically generate CSS rules that are
    useful during development.

    Returns:
        str: A string containing CSS rules.
    """
    return ""


def _render_dev_js(entry: str) -> str:
    """
    Renders the development JavaScript script tags for a given entry file.

    This function generates HTML script tags necessary for loading the specified
    JavaScript entry file in a development environment. It includes a tag for the
    Vite development server client and another for the specified entry file, both
    served from `settings.VITE_DEV_SERVER_URL`.

    Args:
        entry: The path to the entry JavaScript file.

    Returns:
        str: The HTML string containing the script tags for the development
        JavaScript files.
    """
    dev_server_url = settings.VITE_DEV_SERVER_URL.rstrip("/")
    return (
        f'<script type="module" src="{dev_server_url}/@vite/client"></script>'
        f'<script type="module" src="{dev_server_url}/{entry}"></script>'
    )


def _imported_chunks(entry: str) -> list[dict[str, Any]]:
    """
    Collects the chunks an entry imports statically, directly or not.

    With more than one entrypoint Rollup moves shared code to its own chunk, and
    the CSS that code imports goes with it: the manifest lists that CSS on the
    shared chunk, not on the entry. Following `imports` is how the backend
    integration guide recovers it. `dynamicImports` are left out, since those
    load on demand.

    Args:
        entry: The manifest key of the entry chunk.

    Returns:
        list[dict[str, Any]]: Each imported chunk once, dependencies before the
        chunks that import them -- the order Vite uses in the HTML it builds.

    Raises:
        KeyError: If `entry` or one of the imported keys is not in the manifest.
    """
    # a propria entrada entra em `seen` para um ciclo que volte a ela nao a repetir
    seen = {entry}
    chunks: list[dict[str, Any]] = []

    def visit(chunk: dict[str, Any]) -> None:
        for key in chunk.get("imports", []):
            if key in seen:
                continue
            seen.add(key)
            imported = _get_chunk(key)
            visit(imported)
            chunks.append(imported)

    visit(_get_chunk(entry))
    return chunks


def _render_prod_css(entry: str) -> str:
    """
    Renders the production CSS links for a given entry.

    Includes the CSS of every chunk the entry imports, not only the entry's own:
    CSS pulled in by shared code lives on the shared chunk.

    Args:
        entry: The key representing the entry for which CSS files are rendered.

    Returns:
        A string containing the HTML link tags for the CSS files of the given
        entry, each file once, dependencies first.
    """
    chunks = [*_imported_chunks(entry), _get_chunk(entry)]
    # dois chunks podem apontar para o mesmo arquivo de CSS; dict.fromkeys preserva a ordem
    css_files = dict.fromkeys(css_file for chunk in chunks for css_file in chunk.get("css", []))

    return "".join(
        f'<link rel="stylesheet" href="{static(f"dist/{css_file}")}" />' for css_file in css_files
    )


def _render_prod_js(entry: str) -> str:
    """
    Renders the production JavaScript tags for a given entry.

    Emits the entry's module script followed by a `modulepreload` link for each
    imported chunk, so the browser fetches them in parallel instead of
    discovering them one import at a time.

    Args:
        entry: The identifier of the JavaScript module to render.

    Returns:
        A string containing the script tag for the entry and the preload links
        for its imported chunks.
    """
    src = static(f"dist/{_get_chunk(entry)['file']}")
    preloads = "".join(
        f'<link rel="modulepreload" href="{static(f"dist/{chunk['file']}")}" />'
        for chunk in _imported_chunks(entry)
    )
    return f'<script type="module" src="{src}"></script>{preloads}'


@register.simple_tag
def vite_css(entry: str) -> SafeString:
    """
    Registers a template tag to include CSS files using Vite.

    This function dynamically determines the appropriate CSS files to include based
    on the current environment (development or production). It renders the correct
    CSS link elements for templates.

    Args:
        entry: The name of the entry file to link to the relevant CSS assets.

    Returns:
        SafeString: A safe HTML string containing the CSS link elements.
    """
    html = _render_dev_css() if settings.DEBUG else _render_prod_css(entry)
    return mark_safe(html)


@register.simple_tag
def vite_js(entry: str) -> SafeString:
    """
    Renders and returns a JavaScript snippet for Vite integration, varying between
    development or production environments based on the settings.

    In the development environment, this function invokes `_render_dev_js` to generate
    the appropriate JavaScript snippet. In the production environment, it uses
    `_render_prod_js`. The output is marked as safe for rendering in templates
    using `mark_safe`.

    Args:
        entry: The JavaScript entry point name.

    Returns:
        SafeString: The safe HTML string of the JavaScript snippet for inclusion
        in the template.
    """
    html = _render_dev_js(entry) if settings.DEBUG else _render_prod_js(entry)
    return mark_safe(html)


@register.simple_tag
def vite_asset(entry: str) -> str:
    """
    Generates the HTML for including Vite assets by combining CSS and JS assets associated
    with the given entry. Ensures the resulting HTML markup is safe for rendering.

    Args:
        entry: The asset entry point representing the specific file or bundle to be
            included (usually without file extension).

    Returns:
        str: Safe HTML markup containing the combined CSS and JS Vite assets for the given
            entry.
    """
    html = f"{vite_css(entry)}{vite_js(entry)}"
    return mark_safe(html)
