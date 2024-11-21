import datetime

import cv2

from libs.ipc import BasePublisher, BaseSubscriber
from libs.schemas.analysis_msg import AnalysisMsg
from libs.schemas.monitor_msg import ConcentrationStatus, MonitorMsg
from libs.types import MatLike


class App:
    def __init__(
        self,
        monitor_msg_publisher: BasePublisher[MonitorMsg],
        frame_publisher: BasePublisher[MatLike],
        analysis_msg_subscriber: BaseSubscriber[AnalysisMsg],
        *,
        video_path_or_device_id: str | int = 0,
    ) -> None:
        self._monitor_msg_publisher = monitor_msg_publisher
        self._frame_publisher = frame_publisher
        self._analysis_msg_subscriber = analysis_msg_subscriber

        self._video_path_or_device_id = video_path_or_device_id

    def run(self) -> None:
        self._analysis_msg_subscriber.start(self._on_analysis_msg)
        cap = cv2.VideoCapture(self._video_path_or_device_id)

        while 1:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            self._frame_publisher.publish(frame)
            self._publish_monitor_msg()

    def _publish_monitor_msg(self) -> None:
        now = datetime.datetime.now()
        self._monitor_msg_publisher.publish(
            MonitorMsg(
                timestamp=now,
                payload=ConcentrationStatus(
                    overall_score=self._calc_score(),
                    sleeping_confidence=1.0,
                ),
            )
        )

    def _calc_score(self) -> float:
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        return float(hour * 10000 + minute * 100 + second)

    def _on_analysis_msg(self, analysis_msg: AnalysisMsg) -> None:
        print(analysis_msg)
