from abc import ABC, abstractmethod


class BaseChannelSender(ABC):

    @abstractmethod
    def send(self, channel_config, message: str):
        pass
