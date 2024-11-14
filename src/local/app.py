import datetime
import time

from ipc import BasePublisher
from schema import ConcentrationStatus, MonitorMsg


class App:
    def __init__(self, publisher: BasePublisher[MonitorMsg]) -> None:
        self._publisher = publisher

    def run(self) -> None:
        def calc_score() -> float:
            hour = datetime.datetime.now().hour
            minute = datetime.datetime.now().minute
            second = datetime.datetime.now().second
            return float(hour * 10000 + minute * 100 + second)

        while 1:
            now = datetime.datetime.now()
            self._publisher.publish(
                MonitorMsg(
                    timestamp=now,
                    payload=ConcentrationStatus(
                        overall_score=calc_score(),
                        sleeping_confidence=1.0,
                    ),
                )
            )
            time.sleep(5)
