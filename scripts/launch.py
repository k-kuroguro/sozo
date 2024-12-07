import argparse
from threading import Thread

from apps.local import App as LocalApp
from apps.processing import App as ProcessingApp
from apps.web import App as WebApp
from libs.config import read_config
from libs.ipc import (
    AnalysisMsgSerializer,
    ImageSerializer,
    MonitorMsgSerializer,
    ZmqPublisher,
    ZmqSubscriber,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/launch_all.yaml")
    args = parser.parse_args()

    config = read_config(args.config)

    monitor_msg_serializer = MonitorMsgSerializer()
    analysis_msg_serializer = AnalysisMsgSerializer()
    frame_serializer = ImageSerializer()

    apps: list = []

    if config.web.enabled:
        web_params = config.web.parameters
        monitor_msg_subscriber = ZmqSubscriber(
            add_addr_prefix(web_params.monitor_subscriber_addr),
            web_params.monitor_topic,
            monitor_msg_serializer,
        )
        web_app = WebApp(monitor_msg_subscriber)
        apps.append((web_app, {"host": web_params.host, "port": web_params.port}))

    if config.local.enabled:
        local_params = config.local.parameters
        monitor_msg_publisher = ZmqPublisher(
            add_addr_prefix(local_params.monitor_publisher_addr),
            local_params.monitor_topic,
            monitor_msg_serializer,
        )
        frame_publisher = ZmqPublisher(
            add_addr_prefix(local_params.frame_publisher_addr),
            local_params.frame_topic,
            frame_serializer,
        )
        analysis_msg_subscriber = ZmqSubscriber(
            add_addr_prefix(local_params.analysis_subscriber_addr),
            local_params.analysis_topic,
            analysis_msg_serializer,
        )
        local_app = LocalApp(
            monitor_msg_publisher,
            frame_publisher,
            analysis_msg_subscriber,
            video_path_or_device_id=local_params.video_path_or_device_id,
            max_buffer_size=local_params.max_buffer_size,
            ear_threshold=local_params.ear_threshold,
            looking_away_x_threshold=local_params.looking_away_x_threshold,
            looking_away_penalty=local_params.looking_away_penalty,
            head_direction_std_weight=local_params.head_direction_std_weight,
        )
        apps.append((local_app, {}))

    if config.processing.enabled:
        processing_params = config.processing.parameters
        frame_subscriber = ZmqSubscriber(
            add_addr_prefix(processing_params.frame_subscriber_addr),
            processing_params.frame_topic,
            frame_serializer,
        )
        analysis_publisher = ZmqPublisher(
            add_addr_prefix(processing_params.analysis_publisher_addr),
            processing_params.analysis_topic,
            analysis_msg_serializer,
        )
        processing_app = ProcessingApp(frame_subscriber, analysis_publisher)
        apps.append((processing_app, {}))

    threads = []
    for app, kwargs in apps:
        thread = Thread(target=app.run, kwargs=kwargs)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def add_addr_prefix(addr: str) -> str:
    prefix = "ipc://" if addr.startswith("/") else "tcp://"
    return prefix + addr


if __name__ == "__main__":
    main()
