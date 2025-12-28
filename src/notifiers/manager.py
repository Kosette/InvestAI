from .senders.console import ConsoleSender
from .senders.slack import SlackSender
from .senders.webhook import WebhookSender
from config import NOTIFICATION_CONFIG, NotificationConfig


class NotificationManager:

    def __init__(self, config: NotificationConfig):
        self.config = config

        self.senders = {
            "slack": SlackSender(),
            "webhook": WebhookSender(),
            "console": ConsoleSender(),
        }

    def notify(self, message: str):
        if not self.config.enabled:
            return

        for name, channel in self.config.channels.items():
            if not channel.enabled:
                continue

            sender = self.senders.get(channel.type)
            if not sender:
                raise ValueError(f"Unsupported channel type: {channel.type}")

            sender.send(channel, message)

notification_manager = NotificationManager(NOTIFICATION_CONFIG)

if __name__ == "__main__":
    notification_manager.notify("Hello, world!")