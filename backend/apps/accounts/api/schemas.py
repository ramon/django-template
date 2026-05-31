from uuid import UUID

from apps.accounts.models import Profile
from ninja import Schema
from pydantic import HttpUrl


class ProfileOut(Schema):
    id: UUID
    name: str
    gender: str
    avatar: HttpUrl | None
