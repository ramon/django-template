import re
from collections.abc import Callable
from typing import Any

from django.core.files import File
from servestatic.storage import CompressedManifestStaticFilesStorage


class ViteManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Static files storage that leaves the Vite build output under its own names.

    Vite already versions what it writes to `dist/` by content, and its chunks
    import each other by those names (`./shared-Ab12Cd34.js`). Hashing them
    again gives `{% static %}` a second name for the same module, and the browser
    downloads both: the `modulepreload` under one, the `import` under the other.
    Files outside `dist/` keep Django's hash; everything is still compressed.

    Attributes:
        vite_prefix: Path of the Vite output relative to the static root.
    """

    vite_prefix = "dist/"

    def hashed_name(
        self, name: str, content: File[Any] | None = None, filename: str | None = None
    ) -> str:
        if self._is_vite_output(name):
            return name
        # o pai vem do servestatic, sem tipos: a anotacao devolve o str ao mypy
        hashed: str = super().hashed_name(name, content, filename)
        return hashed

    # repassa o resto como veio: a assinatura muda entre versoes do Django (`ignored_blocks`)
    def url_converter(self, name: str, *args: Any, **kwargs: Any) -> Callable[[re.Match[str]], str]:
        if self._is_vite_output(name):
            # o nome do arquivo ja' carrega o hash deste conteudo; reescrever um url()
            # mudaria o arquivo sem mudar o nome, e o cache imutavel serviria o antigo
            return lambda match: match.group(0)
        converter: Callable[[re.Match[str]], str] = super().url_converter(name, *args, **kwargs)
        return converter

    def _is_vite_output(self, name: str) -> bool:
        clean_name: str = self.clean_name(name)
        return clean_name.startswith(self.vite_prefix)
