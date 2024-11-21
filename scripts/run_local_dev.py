import cv2

from apps.local import App as LocalApp
from libs.ipc import BasePublisher, BaseSubscriber
from libs.schemas.analysis_msg import AnalysisMsg
from libs.schemas.monitor_msg import MonitorMsg
from libs.types import Callback, MatLike


class DummyFramePublisher(BasePublisher[MatLike]):
    def publish(self, obj: MatLike) -> None:
        cv2.imshow("frame", obj)
        cv2.waitKey(1)

    def close(self) -> None:
        cv2.destroyAllWindows()


class DummyMonitorMsgPublisher(BasePublisher[MonitorMsg]):
    def publish(self, obj: MonitorMsg) -> None:
        print(obj)

    def close(self) -> None: ...


class DummyAnalysisMsgSubscriber(BaseSubscriber[AnalysisMsg]):
    def start(self, callback: Callback[AnalysisMsg]) -> None: ...

    def close(self) -> None: ...


def main() -> None:
    frame_publisher = DummyFramePublisher()
    monitor_msg_publisher = DummyMonitorMsgPublisher()
    analysis_msg_subscriber = DummyAnalysisMsgSubscriber()
    app = LocalApp(
        monitor_msg_publisher,
        frame_publisher,
        analysis_msg_subscriber,
        video_path_or_device_id="videos/head-pose-face-detection-male.mp4",
    )
    app.run()


if __name__ == "__main__":
    main()
