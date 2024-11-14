import datetime
import time
from random import random
from threading import Thread

from ipc import BaseSubscriber
from schema import ConcentrationStatus, MonitorMsg
from web import App


class StubSubscriber(BaseSubscriber):
    def __init__(self):
        self._thread: Thread | None = None
        self._is_running = False

    def start(self, callback) -> None:
        self._is_running = True
        self._thread = Thread(target=self._run, args=(callback,), daemon=True)
        self._thread.start()

    def _run(self, callback) -> None:
        while self._is_running:
            msg = MonitorMsg(
                timestamp=datetime.datetime.now(),
                payload=ConcentrationStatus(
                    overall_score=random(),
                    sleeping_confidence=random(),
                ),
            )
            callback(msg)
            time.sleep(1)

    def close(self) -> None:
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()


def main() -> None:
    subscriber = StubSubscriber()
    app = App(subscriber)
    app.run(host="0.0.0.0", port=8080, log_level="debug")


if __name__ == "__main__":
    main()
