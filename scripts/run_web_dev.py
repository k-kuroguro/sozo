import datetime
import time
from random import random
from threading import Thread

from apps.web import App
from libs.ipc import BaseSubscriber
from libs.schemas.monitor_msg import ConcentrationStatus, MonitorMsg
from libs.types import Callback


class FakeSubscriber(BaseSubscriber[MonitorMsg]):
    def __init__(self) -> None:
        self._thread: Thread | None = None
        self._is_running = False

    def start(self, callback: Callback[MonitorMsg]) -> None:
        self._is_running = True
        self._thread = Thread(target=self._run, args=(callback,), daemon=True)
        self._thread.start()

    def _run(self, callback: Callback[MonitorMsg]) -> None:
        while self._is_running:
            msg = MonitorMsg(
                timestamp=datetime.datetime.now(),
                payload=ConcentrationStatus(
                    overall_score=random(),
                    sleeping_confidence=random(),
                ),
            )
            callback(msg)
            time.sleep(2)

    def close(self) -> None:
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()


def main() -> None:
    subscriber = FakeSubscriber()
    app = App(subscriber)
    app.run("0.0.0.0", 8080, log_level="debug")


if __name__ == "__main__":
    main()
