from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseSerializer(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, obj: T) -> bytes: ...

    @abstractmethod
    def deserialize(self, data: bytes) -> T: ...
