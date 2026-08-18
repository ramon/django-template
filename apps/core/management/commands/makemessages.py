"""makemessages com os padroes do projeto."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandParser
from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.utils.translation import to_locale

# O padrao do Django ignora "CVS", ".*", "*~" e "*.pyc" -- o que ja cobre .venv,
# mas nao a toolchain de JS nem a saida do Vite.
EXTRA_IGNORE_PATTERNS = [
    "node_modules",
    "static/dist",
    # um teste que afirme algo sobre uma string traduzida injetaria essa string
    # no catalogo; o padrao casa com tests/ na raiz e com apps/<app>/tests/
    "tests",
]


class Command(MakeMessagesCommand):
    """
    Gera os .po sem referencias de linha e sem entradas obsoletas.

    - `--no-location`: sem o par arquivo:linha, que muda a cada refatoracao e
      enche o diff de ruido sem conteudo traduzivel. Para depurar uma string,
      `--add-location=file` volta atras pontualmente.
    - `--no-obsolete`: mensagens que sairam do codigo desaparecem, em vez de
      acumularem comentadas com `#~` ate ninguem saber mais o que e' vivo.
    - sem `-l/-x/-a`, usa os idiomas de `settings.LANGUAGES`;
    - remove `POT-Creation-Date`, que o msgmerge reescreve a cada execucao e
      faria todo `makemessages` sujar os seis catalogos sem mudar traducao
      nenhuma -- e impediria checar no CI se os catalogos estao em dia.

    Onde cada catalogo cai e' decisao do proprio Django: ao encontrar um diretorio
    `locale/` na varredura, ele passa a mandar para la tudo que estiver abaixo do
    diretorio pai. Como cada app tem o seu, as strings do app ficam no app, e o
    `locale/` da raiz recebe apenas o que sobra -- templates/ e config/.
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

        for catalogo in self.catalogos_do_projeto():
            self.remove_data_de_criacao(catalogo)

        return result

    @staticmethod
    def catalogos_do_projeto() -> Iterator[Path]:
        """
        Os .po deste repositorio: LOCALE_PATHS e o locale/ de cada app local.

        O corte e' por APPS_DIR, nao por BASE_DIR: get_app_configs() devolve
        tambem os apps de terceiros, e o .venv fica *dentro* do BASE_DIR -- filtrar
        por ele deixaria passar 700 catalogos em site-packages, que nao sao nossos
        para reescrever.
        """
        apps_dir = Path(settings.BASE_DIR) / "apps"

        raizes = [Path(p) for p in settings.LOCALE_PATHS]
        raizes += [
            Path(app.path) / "locale"
            for app in apps.get_app_configs()
            if Path(app.path).is_relative_to(apps_dir)
        ]

        for raiz in raizes:
            yield from raiz.glob("*/LC_MESSAGES/*.po")

    @staticmethod
    def remove_data_de_criacao(catalogo: Path) -> None:
        linhas = catalogo.read_text(encoding="utf-8").splitlines(keepends=True)
        sem_data = [linha for linha in linhas if not linha.startswith('"POT-Creation-Date:')]

        if len(sem_data) != len(linhas):
            catalogo.write_text("".join(sem_data), encoding="utf-8")
