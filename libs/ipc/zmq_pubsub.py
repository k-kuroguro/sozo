from threading import Thread
from typing import TypeVar

import zmq

from libs.types import Callback

from .base_pubsub import BasePublisher, BaseSubscriber
from .base_serializer import BaseSerializer

Msg = TypeVar("Msg")


class ZmqPublisher(BasePublisher[Msg]):
    def __init__(self, addr: str, topic: str, serializer: BaseSerializer[Msg]) -> None:
        self._topic = topic

        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.PUB)
        self._socket.bind(addr)

        self._serializer = serializer

    def publish(self, msg: Msg) -> None:
        if self._socket.closed:
            raise ValueError("Publisher is closed")

        self._socket.send_multipart([self._topic.encode(), self._serializer.serialize(msg)])

    def close(self) -> None:
        self._socket.close()
        self._ctx.term()


class ZmqSubscriber(BaseSubscriber[Msg]):
    def __init__(self, addr: str, topic: str, serializer: BaseSerializer[Msg]) -> None:
        self._topic = topic
        self._thread: Thread | None = None
        self._is_running = False

        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.SUB)
        self._socket.connect(addr)
        self._socket.subscribe(topic.encode())

        self._serializer = serializer

    def start(self, callback: Callback[Msg]) -> None:
        if self._is_running:
            raise RuntimeError("Subscriber is already running")
        if self._socket.closed:
            raise ValueError("Subscriber is closed")

        self._is_running = True
        self._thread = Thread(target=self._run, args=(callback,), daemon=True)
        self._thread.start()

    def _run(self, callback: Callback[Msg]) -> None:
        poller = zmq.Poller()
        poller.register(self._socket, zmq.POLLIN)
        while self._is_running:
            if self._socket in dict(poller.poll(100)):
                _, msg = self._socket.recv_multipart()
                callback(self._serializer.deserialize(msg))

    def close(self) -> None:
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._socket.close()
        self._ctx.term()
