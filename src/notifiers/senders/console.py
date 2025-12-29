from config.config import ConsoleChannelConfig
from .base import BaseChannelSender
from log import logger

class ConsoleSender(BaseChannelSender):

    def send(self, channel_config: ConsoleChannelConfig, message: str): 
        logger.info(message)
