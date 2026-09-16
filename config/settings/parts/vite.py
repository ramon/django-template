from config.settings.parts.env import env
from config.settings.parts.paths import STATIC_DIR

# Mesma variavel que o docker-compose.yml publica e o vite.config.mjs escuta: trocar
# VITE_PORT no .env move a tag, o compose e o Vite juntos, sem porta para divergir.
VITE_PORT = env.int("VITE_PORT", default=8001)

# URL que o browser usa para pedir os assets em DEBUG. So precisa ser definida quando
# o dev server nao esta em 127.0.0.1 (outro host, proxy); fora isso, VITE_PORT basta.
VITE_DEV_SERVER_URL = env.str("VITE_DEV_SERVER_URL", default=f"http://127.0.0.1:{VITE_PORT}")

# Onde a tag le o manifest fora de DEBUG. O loader padrao le o arquivo em
# VITE_MANIFEST_PATH; aponte VITE_MANIFEST_LOADER para outra funcao sem argumentos que
# devolva o manifest ja' parseado quando ele nao estiver no disco (bucket, CDN).
VITE_MANIFEST_PATH = STATIC_DIR / "dist" / ".vite" / "manifest.json"
VITE_MANIFEST_LOADER = "apps.core.templatetags.vite.read_manifest_file"

__all__ = [
    "VITE_DEV_SERVER_URL",
    "VITE_MANIFEST_LOADER",
    "VITE_MANIFEST_PATH",
    "VITE_PORT",
]
