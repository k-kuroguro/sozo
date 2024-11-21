from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from libs.types import Callback

Msg = TypeVar("Msg")


class BasePublisher(Generic[Msg], metaclass=ABCMeta):
    @abstractmethod
    def publish(self, msg: Msg) -> None:
        """Publish a message to subscribers.

        Raises:
            ValueError: If the communication channel is already closed.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the communication channel."""
        ...


class BaseSubscriber(Generic[Msg], metaclass=ABCMeta):
    @abstractmethod
    def start(self, callback: Callback[Msg]) -> None:
        """Begin an event loop to handle incoming messages.

        This must be called at most once.
        The event loop should run asynchronously, meaning the start method must not block subsequent operations.

        Args:
            callback (Callback[Msg]): Function to call when a message is received.

        Raises:
            RuntimeError: If this method is called more than once.
            ValueError: If the communication channel is already closed.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """End an event loop and close the communication channel."""
        ...
