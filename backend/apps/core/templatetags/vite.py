import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe, SafeString

register = template.Library()

VITE_DEV_SERVER_URL = "http://127.0.0.1:8001"


def _manifest_path() -> Path:
    """
    Retrieves the path to the Vite manifest file.

    The function constructs and returns the path to the Vite manifest file,
    which is located in the "static/dist/.vite" directory relative to the
    project's base directory.

    Returns:
        Path: A `Path` object pointing to the Vite manifest file.
    """
    return settings.BASE_DIR / "static" / "dist" / ".vite" / "manifest.json"


@lru_cache(maxsize=1)
def _load_manifest() -> dict[str, Any]:
    """
    Loads and caches a JSON manifest file.

    This function is designed to read and parse a JSON manifest file from a predefined
    path. The function utilizes an LRU cache with a maximum size of 1 to ensure the
    manifest is only loaded and parsed once during the application's lifecycle, unless
    the cache is explicitly cleared. This improves performance by avoiding redundant
    disk I/O and parsing operations.

    Returns:
        dict[str, Any]: The parsed JSON content of the manifest file.

    Raises:
        JSONDecodeError: If the file's contents cannot be parsed into a valid JSON object.
        FileNotFoundError: If the manifest file does not exist at the expected location.
    """
    manifest_path = _manifest_path()
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _get_chunk(entry: str) -> dict[str, Any]:
    manifest = _load_manifest()
    return manifest[entry]


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
    Vite development server client and another for the specified entry file.

    Args:
        entry (str): The path to the entry JavaScript file.

    Returns:
        str: The HTML string containing the script tags for the development
        JavaScript files.
    """
    return (
        f'<script type="module" src="{VITE_DEV_SERVER_URL}/@vite/client"></script>'
        f'<script type="module" src="{VITE_DEV_SERVER_URL}/{entry}"></script>'
    )


def _render_prod_css(entry: str) -> str:
    """
    Renders the production CSS links for a given entry.

    This function takes an entry key, retrieves the corresponding CSS files,
    and formats them into HTML link tags referencing the static path of the
    production CSS files.

    Args:
        entry: The key representing the entry for which CSS files are rendered.

    Returns:
        A string containing the HTML link tags for the CSS files of the given
        entry.
    """
    chunk = _get_chunk(entry)
    css_files: list[str] = chunk.get("css", [])

    return "".join(
        f'<link rel="stylesheet" href="{static(f"dist/{css_file}")}" />'
        for css_file in css_files
    )


def _render_prod_js(entry: str) -> str:
    """
    Renders the production JavaScript script tag for a given entry.

    The function takes an entry identifier, retrieves the associated chunk file,
    and generates a string containing an HTML script tag for including the
    specified JavaScript file in production mode.

    Args:
        entry: The identifier of the JavaScript module to render.

    Returns:
        A string containing the HTML script tag for the specified JavaScript entry.
    """
    chunk = _get_chunk(entry)
    return f'<script type="module" src="{static(f"dist/{chunk["file"]}")}" />'


@register.simple_tag
def vite_css(entry: str) -> SafeString:
    """
    Registers a template tag to include CSS files using Vite.

    This function dynamically determines the appropriate CSS files to include based
    on the current environment (development or production). It renders the correct
    CSS link elements for templates.

    Args:
        entry (str): The name of the entry file to link to the relevant CSS assets.

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
        entry (str): The JavaScript entry point name.

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
        entry (str): The asset entry point representing the specific file or bundle to be
            included (usually without file extension).

    Returns:
        str: Safe HTML markup containing the combined CSS and JS Vite assets for the given
            entry.
    """
    html = f"{vite_css(entry)}{vite_js(entry)}"
    return mark_safe(html)
