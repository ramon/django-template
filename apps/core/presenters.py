from typing import Any, Self


class BasePresenter[T]:
    """
    BasePresenter provides a generic interface for adapting objects.

    This class is designed to act as a wrapper around objects of any type, enabling
    dynamic adaptation of their attributes and providing utilities like handling
    collections of objects. It allows seamless access to the underlying object's
    attributes while enabling additional customization.

    Attributes:
        obj: The object the presenter wraps around.
    """

    obj: T

    def __init__(self, obj: T):
        self.obj = obj

    def __getattr__(self, name: str) -> Any:
        return getattr(self.obj, name)

    @classmethod
    def collection(cls, objs: list[T]) -> list[Self]:
        return [cls(obj) for obj in objs]
