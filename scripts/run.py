from threading import Thread

from apps.local import App as LocalApp
from apps.processing import App as ProcessingApp
from apps.web import App as WebApp
from libs.ipc import (
    AnalysisMsgSerializer,
    ImageSerializer,
    MonitorMsgSerializer,
    ZmqPublisher,
    ZmqSubscriber,
)


def main() -> None:
    socket_addr = "ipc:///tmp/sozo"

    monitor_topic = "monitoring"
    monitor_msg_serializer = MonitorMsgSerializer()
    monitor_msg_publisher = ZmqPublisher(socket_addr, monitor_topic, monitor_msg_serializer)
    monitor_msg_subscriber = ZmqSubscriber(socket_addr, monitor_topic, monitor_msg_serializer)

    frame_topic = "frame"
    frame_serializer = ImageSerializer()
    frame_publisher = ZmqPublisher(socket_addr, frame_topic, frame_serializer)
    frame_subscriber = ZmqSubscriber(socket_addr, frame_topic, frame_serializer)

    analysis_topic = "analysis"
    analysis_msg_serializer = AnalysisMsgSerializer()
    analysis_msg_publisher = ZmqPublisher(socket_addr, analysis_topic, analysis_msg_serializer)
    analysis_msg_subscriber = ZmqSubscriber(socket_addr, analysis_topic, analysis_msg_serializer)

    web_app = WebApp(monitor_msg_subscriber)
    local_app = LocalApp(monitor_msg_publisher, frame_publisher, analysis_msg_subscriber)
    processing_app = ProcessingApp(frame_subscriber, analysis_msg_publisher)

    web_thread = Thread(
        target=web_app.run,
        kwargs={"host": "0.0.0.0", "port": 8080},
    )
    local_thread = Thread(target=local_app.run)
    processing_thread = Thread(target=processing_app.run)

    web_thread.start()
    local_thread.start()
    processing_thread.start()

    web_thread.join()
    local_thread.join()
    processing_thread.join()


if __name__ == "__main__":
    main()
