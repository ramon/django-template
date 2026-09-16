from pathlib import Path

import pytest
from django.core.management import call_command


@pytest.fixture
def collect_static(tmp_path, settings):
    """
    Runs `collectstatic` with the production static files storage.

    The test settings swap in `StaticFilesStorage`, which never hashes, so the
    difference between the name Vite writes and the name `{% static %}` returns
    only shows with the real storage and a real collect.

    Returns:
        A function that writes the given files (path relative to the static
        source dir -> content) and collects them, returning `STATIC_ROOT`.
    """

    def collect(files):
        source = tmp_path / "source"
        for name, content in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        settings.STATICFILES_DIRS = [source]
        # so' os arquivos do teste: o AppDirectoriesFinder traria o admin inteiro
        settings.STATICFILES_FINDERS = [
            "django.contrib.staticfiles.finders.FileSystemFinder",
        ]
        settings.STATIC_ROOT = tmp_path / "public"
        settings.STORAGES = {
            **settings.STORAGES,
            "staticfiles": {"BACKEND": "apps.core.storage.ViteManifestStaticFilesStorage"},
        }
        call_command("collectstatic", interactive=False, verbosity=0)
        return Path(settings.STATIC_ROOT)

    return collect
