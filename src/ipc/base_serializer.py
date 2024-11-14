from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

Msg = TypeVar("Msg")


class BaseSerializer(Generic[Msg], metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, msg: Msg) -> bytes: ...

    @abstractmethod
    def deserialize(self, data: bytes) -> Msg: ...
