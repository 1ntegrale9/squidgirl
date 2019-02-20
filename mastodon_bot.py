import os
import random
from mastodon import Mastodon
from mastodon import StreamListener
from scrapbox_client import getDescriptions


class StreamClient(StreamListener):
    def __init__(self, client):
        self.client = client
        super().__init__()

    def on_notification(self, notification):
        if notification['type'] == 'mention':
            id = notification['account']['username']
            msg = random.choice(getDescriptions('squidgirl', 'reply'))
            status = f'@{id} {msg}'
            self.client.status_post(status, in_reply_to_id=notification['status'], visibility='unlisted')


def job():
    client = Mastodon(
        access_token=os.environ['MASTODON_TOKEN'],
        api_base_url='ika.queloud.net',
    )
    client.stream_user(StreamClient(client))


if __name__ == '__main__':
    job()
