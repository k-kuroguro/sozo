import time
from threading import Thread

import cv2

from apps.processing.app import App as ProcessingApp
from libs.ipc import BasePublisher, BaseSubscriber
from libs.schemas.analysis_msg import AnalysisMsg
from libs.types import Callback, MatLike


class DummyFrameSubscriber(BaseSubscriber[MatLike]):
    def __init__(self, video_path: str) -> None:
        self._thread: Thread | None = None
        self._is_running = False
        self._cap = cv2.VideoCapture(video_path)
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)

    def start(self, callback: Callback[MatLike]) -> None:
        self._is_running = True
        self._thread = Thread(target=self._run, args=(callback,), daemon=True)
        self._thread.start()

    def _run(self, callback: Callback[MatLike]) -> None:
        prev_time = time.time()
        while self._is_running:
            ret, frame = self._cap.read()
            if not ret:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            callback(frame)

            time.sleep(max(0, 1 / self._fps - (time.time() - prev_time)))
            prev_time = time.time()

    def close(self) -> None:
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._cap.release()


class DummyAnalysisMsgPublisher(BasePublisher[AnalysisMsg]):
    def publish(self, obj: AnalysisMsg) -> None:
        print(obj)

    def close(self) -> None: ...


def main() -> None:
    frame_subscriber = DummyFrameSubscriber("videos/head-pose-face-detection-male.mp4")
    analysis_msg_publisher = DummyAnalysisMsgPublisher()
    app = ProcessingApp(frame_subscriber, analysis_msg_publisher)
    app.run()


if __name__ == "__main__":
    main()
