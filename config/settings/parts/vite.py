from config.settings.parts.env import env

# Mesma variavel que o docker-compose.yml publica e o vite.config.mjs escuta: trocar
# VITE_PORT no .env move a tag, o compose e o Vite juntos, sem porta para divergir.
VITE_PORT = env.int("VITE_PORT", default=8001)

# URL que o browser usa para pedir os assets em DEBUG. So precisa ser definida quando
# o dev server nao esta em 127.0.0.1 (outro host, proxy); fora isso, VITE_PORT basta.
VITE_DEV_SERVER_URL = env.str("VITE_DEV_SERVER_URL", default=f"http://127.0.0.1:{VITE_PORT}")

__all__ = ["VITE_DEV_SERVER_URL", "VITE_PORT"]
