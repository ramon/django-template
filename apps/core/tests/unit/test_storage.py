import re

import pytest
from django.contrib.staticfiles.storage import staticfiles_storage

# repetitive enough for the compressor to consider the result worth keeping
JS = "export const shared = 'shared';\n" * 50
CSS = "@font-face{font-family:x;src:url(./font-abc12345.woff2)}\n.a{color:red}\n" * 20

FILES = {
    "dist/assets/app-a1b2c3d4.js": 'import "./shared-e5f6g7h8.js";\n' + JS,
    "dist/assets/shared-e5f6g7h8.js": JS,
    "dist/assets/app-a1b2c3d4.css": CSS,
    "dist/assets/font-abc12345.woff2": "font",
    "img/logo.svg": "<svg></svg>",
    "css/site.css": ".logo{background:url(../img/logo.svg)}\n" * 20,
}

DJANGO_HASH = re.compile(r"\.[0-9a-f]{12}\.")


@pytest.fixture(autouse=True)
def static_root(collect_static):
    return collect_static(FILES)


@pytest.mark.parametrize(
    "name",
    [
        "dist/assets/app-a1b2c3d4.js",
        "dist/assets/shared-e5f6g7h8.js",
        "dist/assets/app-a1b2c3d4.css",
    ],
)
def test_vite_output_keeps_its_original_name(name):
    assert staticfiles_storage.url(name) == f"/static/{name}"


def test_vite_output_gets_no_django_hashed_copy(static_root):
    """Nobody requests those copies: the chunks import each other by Vite's name."""
    dist = [p.name for p in (static_root / "dist").rglob("*")]

    assert not [name for name in dist if DJANGO_HASH.search(name)]


def test_vite_output_is_still_compressed(static_root):
    assert (static_root / "dist/assets/shared-e5f6g7h8.js.gz").exists()


def test_vite_css_is_left_as_vite_wrote_it(static_root):
    """The name carries a hash of this content; rewriting it would break that."""
    css = (static_root / "dist/assets/app-a1b2c3d4.css").read_text(encoding="utf-8")

    assert css == CSS


@pytest.mark.parametrize("name", ["img/logo.svg", "css/site.css"])
def test_files_outside_dist_keep_the_django_hash(static_root, name):
    url = staticfiles_storage.url(name)

    assert DJANGO_HASH.search(url)
    assert (static_root / url.removeprefix("/static/")).exists()


def test_css_outside_dist_still_points_to_hashed_urls(static_root):
    css_name = staticfiles_storage.url("css/site.css").removeprefix("/static/")
    logo_name = staticfiles_storage.url("img/logo.svg").removeprefix("/static/")

    css = (static_root / css_name).read_text(encoding="utf-8")

    assert f'url("../{logo_name}")' in css
