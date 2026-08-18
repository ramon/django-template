"""makemessages with the project's defaults."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandParser
from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.utils.translation import to_locale

# Django's default ignores "CVS", ".*", "*~" and "*.pyc" -- which already covers
# .venv, but not the JS toolchain nor Vite's output.
EXTRA_IGNORE_PATTERNS = [
    "node_modules",
    "static/dist",
    # a test asserting on a translated string would inject that string into the
    # catalog; the pattern matches tests/ at the root and apps/<app>/tests/
    "tests",
]


class Command(MakeMessagesCommand):
    """
    Generates .po files without line references and without obsolete entries.

    - `--no-location`: no file:line pair, which changes on every refactor and
      fills the diff with noise that carries no translatable content. To debug
      a string, `--add-location=file` opts back in for a moment.
    - `--no-obsolete`: messages removed from the code disappear instead of
      piling up commented out with `#~` until no one knows what's still alive.
    - no `-l/-x/-a`, uses the languages from `settings.LANGUAGES`;
    - strips `POT-Creation-Date`, which msgmerge rewrites on every run and would
      make every `makemessages` dirty the six catalogs without changing a single
      translation -- and would make it impossible for CI to check whether the
      catalogs are up to date.

    Where each catalog lands is Django's own decision: once it finds a `locale/`
    directory during the scan, it routes everything below that directory's
    parent there. Since every app has its own, app strings stay in the app, and
    the root `locale/` only receives what's left over -- templates/ and config/.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.set_defaults(no_location=True, no_obsolete=True)

    def handle(self, *args: Any, **options: Any) -> str | None:
        options["ignore_patterns"] = [
            *(options.get("ignore_patterns") or []),
            *EXTRA_IGNORE_PATTERNS,
        ]

        if not options["locale"] and not options["exclude"] and not options["all"]:
            options["locale"] = [to_locale(code) for code, _ in settings.LANGUAGES]

        result: str | None = super().handle(*args, **options)

        for catalog in self.project_catalogs():
            self.strip_creation_date(catalog)

        return result

    @staticmethod
    def project_catalogs() -> Iterator[Path]:
        """
        The .po files of this repository: LOCALE_PATHS and every local app's locale/.

        The cutoff is by APPS_DIR, not BASE_DIR: get_app_configs() also returns
        third-party apps, and .venv sits *inside* BASE_DIR -- filtering by that
        would let through 700 catalogs in site-packages, which are not ours to
        rewrite.
        """
        apps_dir = Path(settings.BASE_DIR) / "apps"

        roots = [Path(p) for p in settings.LOCALE_PATHS]
        roots += [
            Path(app.path) / "locale"
            for app in apps.get_app_configs()
            if Path(app.path).is_relative_to(apps_dir)
        ]

        for root in roots:
            yield from root.glob("*/LC_MESSAGES/*.po")

    @staticmethod
    def strip_creation_date(catalog: Path) -> None:
        lines = catalog.read_text(encoding="utf-8").splitlines(keepends=True)
        without_date = [line for line in lines if not line.startswith('"POT-Creation-Date:')]

        if len(without_date) != len(lines):
            catalog.write_text("".join(without_date), encoding="utf-8")
