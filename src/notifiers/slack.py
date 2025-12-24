from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from config import Config

client = WebClient(
    token=Config.SLACK_TOKEN)


def send_slack_msg(content, channel="#news"):
    try:
        response = client.chat_postMessage(channel=channel,
                                           text=content)
        # print(response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


if __name__ == "__main__":
    content = json.dumps({'hello': 'world'})
    send_slack_msg(content)
