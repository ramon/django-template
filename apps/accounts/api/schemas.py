from uuid import UUID

from ninja import Schema
from pydantic import Field, HttpUrl


class UserInfoOut(Schema):
    sub: UUID = Field(alias='id')
    name: str
    given_name: str = Field(alias='first_name')
    family_name: str = Field(alias='last_name')
    picture: HttpUrl | None = Field(alias='avatar', default=None)
    email: str
