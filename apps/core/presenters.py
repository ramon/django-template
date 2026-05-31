from typing import TypeVar, Generic, Self

T = TypeVar('T')

class BasePresenter(Generic[T]):
    """
    BasePresenter provides a generic interface for adapting objects.

    This class is designed to act as a wrapper around objects of any type, enabling
    dynamic adaptation of their attributes and providing utilities like handling
    collections of objects. It allows seamless access to the underlying object's
    attributes while enabling additional customization.

    Attributes:
        _obj: The object the presenter wraps around.
    """
    obj: T

    def __init__(self, obj: T):
        self.obj = obj

    def __getattr__(self, name):
        return getattr(self.obj, name)

    @classmethod
    def collection(cls: T, objs: list[T]) -> list[T]:
        return [cls(obj) for obj in objs]
