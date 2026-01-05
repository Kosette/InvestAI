import requests
from config.config import WebhookChannelConfig
from .base import BaseChannelSender


class WebhookSender(BaseChannelSender):
    def send(self, channel_config: WebhookChannelConfig, message: str):
        for endpoint in channel_config.endpoints:
            payload = {"msg_type": "text", "content": {"text": message}}

            resp = requests.post(
                endpoint.url,
                json=payload,
                timeout=5,
            )

            if not resp.ok:
                raise RuntimeError(f"Webhook [{endpoint.name}] failed: {resp.text}")
