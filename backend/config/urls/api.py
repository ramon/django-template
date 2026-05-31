import orjson
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer
from ninja.security import django_auth


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, **kwargs):
        return orjson.dumps(data)


api = NinjaAPI(
    version="1.0.0",
    auth=[django_auth],
    renderer=ORJSONRenderer(),
)

__all__ = ["api"]
