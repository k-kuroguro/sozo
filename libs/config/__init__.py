from .schemas import Config


def read_config(config_file: str) -> Config:
    return Config.from_yaml_file(config_file)

__all__ = ["Config", "read_config"]
