import tomllib
from typing import Any


class Config:
    _config: dict[str, Any] | None = None


    @staticmethod
    def _read_config():
        try:
            with open("config.toml", "rb") as file: # tomllib uses binary; config in working directory
                Config._config = tomllib.load(file)
        except FileNotFoundError:
            Config._config = {}
            print("Configuration file could not be found, using defaults")


    @staticmethod
    def _get_recursive(key: str, dict: dict[str, Any], default: Any) -> Any:
        if dict is None:
            return default

        location = key.split('.', 1)

        if len(location) > 1 and location[0] in dict.keys():
            return Config._get_recursive(location[1], dict[location[0]], default)
        if len(location) == 1:
            return dict.get(key, default)
        return default


    @staticmethod
    def _has_recursive(key: str, dict: dict[str, Any]) -> bool:
        if dict is None:
            return False
        
        location = key.split('.', 1)
        
        if len(location) > 1 and location[0] in dict.keys():
            return Config._has_recursive(location[1], dict[location[0]])
        if len(location) == 1:
            return location[0] in dict.keys()
        return False


    @staticmethod
    def get(key: str, default: Any = None, passed: Any = None) -> Any:
        if passed is not None:
            return passed

        if Config._config is None:
            Config._read_config()

        return Config._get_recursive(key, Config._config, default)

    @staticmethod
    def has(key: str) -> bool:
        if Config._config is None:
            Config._read_config()
        
        return Config._has_recursive(key, Config._config)
