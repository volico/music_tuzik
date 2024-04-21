# -*- coding: utf-8 -*-
from typing import Tuple, Type

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class EnvSettings(BaseSettings):
    ENV_FILE: str = ""


class AppSettings(BaseSettings):

    TOKEN: str = ""  # bot's token
    download_path: str = "./audio"
    max_queue_size: int = 30  # max number of tracks in queue
    command_prefix: str = "/"
    messages: dict = {
        "not_in_voice_channel": "I'm not in a voice channel",
        "user_not_in_voice_channel": "You are not in a voice channel",
        "unsupported_url": "Unsupported url",
        "queue_full": "Queue is full, please wait fors track to finish",
        "start_playing": "{} plays: '{}'",
        "move_to_another_channel": "Bot was moved to {} channel",
    }

    def get_messages(self) -> dict:
        return self.messages

    class Config:
        env_file = EnvSettings().ENV_FILE

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return dotenv_settings, env_settings, init_settings, file_secret_settings
