from config.config import ConsoleChannelConfig
from .base import BaseChannelSender


class ConsoleSender(BaseChannelSender):

    def send(self, channel_config: ConsoleChannelConfig, message: str): 
        print(message)
