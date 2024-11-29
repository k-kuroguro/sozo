from dataclasses import dataclass

from dataclass_wizard import YAMLWizard


@dataclass(slots=True, frozen=True)
class WebParameters:
    host: str
    port: int
    monitor_subscriber_addr: str
    monitor_topic: str


@dataclass(slots=True, frozen=True)
class LocalParameters:
    monitor_publisher_addr: str
    monitor_topic: str
    frame_publisher_addr: str
    frame_topic: str
    analysis_subscriber_addr: str
    analysis_topic: str
    video_path_or_device_id: str | int = 0


@dataclass(slots=True, frozen=True)
class ProcessingParameters:
    frame_subscriber_addr: str
    frame_topic: str
    analysis_publisher_addr: str
    analysis_topic: str


@dataclass(slots=True, frozen=True)
class AppConfig:
    enabled: bool


@dataclass(slots=True, frozen=True)
class WebConfig(AppConfig):
    parameters: WebParameters


@dataclass(slots=True, frozen=True)
class LocalConfig(AppConfig):
    parameters: LocalParameters


@dataclass(slots=True, frozen=True)
class ProcessingConfig(AppConfig):
    parameters: ProcessingParameters


@dataclass(slots=True, frozen=True)
class Config(YAMLWizard):
    web: WebConfig
    local: LocalConfig
    processing: ProcessingConfig
