import tomllib
from typing import Any
from pathlib import Path
from importlib.resources import files

from platformdirs import user_config_dir


class Config:
    _config: dict[str, Any] | None = None
    _global_config = Path(user_config_dir("gww", ensure_exists=True)) / "config.toml"


    @staticmethod
    def reset() -> Path:
        Config._global_config.write_bytes((files("gww") / "config.toml").read_bytes()) # Copy the default from the package to the global config

        return Config._global_config


    @staticmethod
    def _read_config():
        try:
            with open("config.toml", "rb") as file: # tomllib uses binary; config from working directory
                Config._config = tomllib.load(file)
        except FileNotFoundError:
            if not Config._global_config.exists():
                print(f"Global configuration file could not be found, copied default to '{Config.reset()}'")

            with open(Config._global_config, "rb") as file:
                Config._config = tomllib.load(file)


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
