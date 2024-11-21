import os
import time

import cv2

from libs.ipc import BasePublisher, BaseSubscriber
from libs.schemas.analysis_msg import AnalysisMsg
from libs.types import MatLike

from .constants import MODELS_DIR
from .face_detector import FaceDetector
from .facial_landmarks_detector import FacialLandmarksDetector
from .head_pose_estimator import HeadPoseEstimator

SLEEP_INTERVAL = 0.01


class App:
    def __init__(
        self,
        frame_subscriber: BaseSubscriber[MatLike],
        analysis_msg_publisher: BasePublisher[AnalysisMsg],
        *,
        max_buffer_size: int = 3,
    ) -> None:
        self._frame_subscriber = frame_subscriber
        self._analysis_msg_publisher = analysis_msg_publisher

        self._face_detector = FaceDetector(
            os.path.join(MODELS_DIR, "opencv_face_detector_uint8.pb"),
            os.path.join(MODELS_DIR, "opencv_face_detector.pbtxt"),
        )
        self._facial_landmarks_detector = FacialLandmarksDetector(
            os.path.join(MODELS_DIR, "shape_predictor_68_face_landmarks_GTX.dat")
        )
        self._head_pose_estimator = HeadPoseEstimator(
            os.path.join(MODELS_DIR, "facial_landmarks_3d.csv")
        )

        self._prev_time: float = time.time()
        self._fps: float = 0

        self._latest_frame: MatLike | None = None

    def run(self) -> None:
        self._frame_subscriber.start(self._on_frame)
        while 1:
            if self._latest_frame is not None:
                self._process_frame(self._latest_frame.copy())
            else:
                time.sleep(SLEEP_INTERVAL)

    def _on_frame(self, frame: MatLike) -> None:
        self._latest_frame = frame

    def _process_frame(self, frame: MatLike) -> None:
        faces = self._face_detector.detect(frame)
        for face in faces:
            x, y, w, h, _ = face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if faces:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            largest_face = max(faces, key=lambda f: f.area)
            landmarks = self._facial_landmarks_detector.detect(gray, largest_face)

            for x, y in landmarks:
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

            if not self._head_pose_estimator.is_image_size_set():
                self._head_pose_estimator.set_image_size(*frame.shape[:2])
            pose = self._head_pose_estimator.estimate(landmarks).to_direction()

            nose_tip_2d = landmarks[30]
            end_point = (
                int(nose_tip_2d[0] + pose.x * 20),
                int(nose_tip_2d[1] + pose.y * 20),
            )
            cv2.arrowedLine(frame, tuple(nose_tip_2d), end_point, (0, 0, 255), 2)

            self._analysis_msg_publisher.publish(AnalysisMsg(pose))

        curr_time = time.time()
        elapsed_time = curr_time - self._prev_time
        if elapsed_time > 0:
            self._fps = 1 / elapsed_time
        self._prev_time = curr_time
        cv2.putText(
            frame, f"FPS: {self._fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
        )

        cv2.imshow("frame", frame)
        cv2.waitKey(1)
