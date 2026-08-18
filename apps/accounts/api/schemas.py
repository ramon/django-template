from uuid import UUID

from ninja import Schema
from pydantic import Field


class UserInfoOut(Schema):
    sub: UUID = Field(alias="id")
    name: str
    given_name: str = Field(alias="first_name")
    family_name: str = Field(alias="last_name")
    # avatar_url, nao avatar: o campo cru e' um caminho relativo (/media/...), que
    # nao passa por HttpUrl, e o fallback de gravatar do AvatarMixin ficava morto.
    picture: str = Field(alias="avatar_url")
    email: str
