from collections import deque
from datetime import datetime, timedelta
from typing import Deque

import cv2
import numpy as np

from libs.ipc import BasePublisher, BaseSubscriber
from libs.schemas.analysis_msg import AnalysisMsg
from libs.schemas.monitor_msg import ConcentrationStatus, MonitorMsg, PenaltyFactor
from libs.types import MatLike

CLEAR_BUFFER_INTERVAL = timedelta(seconds=1)


class App:
    def __init__(
        self,
        monitor_msg_publisher: BasePublisher[MonitorMsg],
        frame_publisher: BasePublisher[MatLike],
        analysis_msg_subscriber: BaseSubscriber[AnalysisMsg],
        *,
        video_path_or_device_id: str | int = 0,
        max_buffer_size: int = 10,
        ear_threshold: float = 0.25,
        looking_away_x_threshold: float = 25.0,
        looking_away_penalty: float = 50.0,
        head_direction_std_weight: float = 50.0,
    ) -> None:
        self._monitor_msg_publisher = monitor_msg_publisher
        self._frame_publisher = frame_publisher
        self._analysis_msg_subscriber = analysis_msg_subscriber

        self._video_path_or_device_id = video_path_or_device_id
        self._max_buffer_size = max_buffer_size
        self._ear_threshold = ear_threshold
        self._looking_away_x_threshold = looking_away_x_threshold
        self._looking_away_penalty = looking_away_penalty
        self._head_direction_std_weight = head_direction_std_weight

        self._analysis_msg_buffer: Deque[AnalysisMsg] = deque(maxlen=max_buffer_size)

    def run(self) -> None:
        self._analysis_msg_subscriber.start(self._on_analysis_msg)
        cap = cv2.VideoCapture(self._video_path_or_device_id)

        while 1:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if len(self._analysis_msg_buffer) > 0:
                latest = self._analysis_msg_buffer[-1]
                if datetime.now() - latest.timestamp > CLEAR_BUFFER_INTERVAL:
                    self._analysis_msg_buffer.clear()

            self._frame_publisher.publish(frame)
            self._publish_monitor_msg()

    def _publish_monitor_msg(self) -> None:
        score, factor = self._calc_score()
        self._monitor_msg_publisher.publish(
            MonitorMsg(
                timestamp=datetime.now(),
                payload=ConcentrationStatus(overall_score=score, penalty_factor=factor),
            )
        )

    def _calc_score(self) -> tuple[float, PenaltyFactor]:
        if len(self._analysis_msg_buffer) == 0:
            return (0.0, PenaltyFactor.NONE)

        if all(msg.is_absent for msg in self._analysis_msg_buffer):
            return (0.0, PenaltyFactor.IS_ABSENT)

        ears = np.array(
            [
                [msg.both_eye_aspect_ratio.left, msg.both_eye_aspect_ratio.right]
                for msg in self._analysis_msg_buffer
                if msg.both_eye_aspect_ratio
            ]
        )
        if len(ears) >= 0.8 * self._max_buffer_size and self._check_drowsiness(ears):
            return (0.0, PenaltyFactor.IS_DROWSY)

        score = 100.0
        factor = PenaltyFactor.NONE

        head_directions = np.array(
            [
                [msg.head_direction.x, msg.head_direction.y]
                for msg in self._analysis_msg_buffer
                if msg.head_direction
            ]
        )
        head_direction_mean = np.mean(head_directions, axis=0)
        is_head_down = head_direction_mean[1] < 0.0
        if not is_head_down and abs(head_direction_mean[0]) >= self._looking_away_x_threshold:
            score -= self._looking_away_penalty
            factor |= PenaltyFactor.IS_LOOKING_AWAY

        head_direction_std = np.std(head_directions, axis=0)
        score -= self._head_direction_std_weight * float(np.mean(head_direction_std / 20))

        return (max(0.0, min(100.0, score)), factor)

    def _on_analysis_msg(self, analysis_msg: AnalysisMsg) -> None:
        self._analysis_msg_buffer.append(analysis_msg)

    def _check_drowsiness(self, ears: np.ndarray) -> bool:
        half_len = 0.5 * len(ears)
        return (
            len(ears[ears[:, 0] < self._ear_threshold]) >= half_len
            or len(ears[ears[:, 1] < self._ear_threshold]) >= half_len
        )
