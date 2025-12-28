from slack_sdk import WebClient
from config.config import SlackChannelConfig
from .base import BaseChannelSender
from slack_sdk.errors import SlackApiError
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from loguru import logger


class SlackSender(BaseChannelSender):

    def send(self, channel_config: SlackChannelConfig, message: str):
        logger.debug(f"SlackSender send message: {channel_config.token}, {channel_config.default_channel}, {message}")
        client = WebClient(token=channel_config.token)

        try:
            response = client.chat_postMessage(channel=channel_config.default_channel,
                                            text=message)
            # print(response)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            # str like 'invalid_auth', 'channel_not_found'
            assert e.response["error"]
            print(f"Got an error: {e.response['error']}")

