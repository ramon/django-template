"""Project-specific compilemessages: bakes in the ignore patterns the native command lacks."""

from typing import Any

from django.core.management.commands.compilemessages import (
    Command as CompileMessagesCommand,
)

# ao contrario do makemessages, o nativo aqui nao ignora nada por padrao -- sem
# isto ele varre o .venv inteiro (catalogos de dependencias) e qualquer
# node_modules presente na maquina.
EXTRA_IGNORE_PATTERNS = [".venv", "node_modules"]


class Command(CompileMessagesCommand):
    """Compile .po files to .mo, ignoring .venv and node_modules by default.

    The native command walks the tree from the current directory looking for
    `locale/` folders; without `--ignore`, that includes `.venv` and any
    `node_modules` present. See docs/standards/i18n.md.
    """

    def handle(self, **options: Any) -> None:
        options["ignore_patterns"] = [
            *(options.get("ignore_patterns") or []),
            *EXTRA_IGNORE_PATTERNS,
        ]
        super().handle(**options)
