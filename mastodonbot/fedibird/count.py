import os
from mastodon import Mastodon
from argparse import ArgumentParser


def fedibird():
    return Mastodon(
        access_token=os.getenv('MASTODON_TOKEN'),
        api_base_url='https://fedibird.com',
    )


def count(time):
    client = fedibird()
    statuses = sorted(
        client.account_statuses(77150),
        key=lambda status: status['created_at'],
        reverse=True,
    )
    status = [status for status in statuses if status['poll'] is not None][0]
    status_poll = status['poll']
    votes = [poll['votes_count'] for poll in status_poll['options'] if poll['title'] == f'{time}時から参加可能'][0]

    client.status_post(
        status=f'{time}時から{votes}人が参加できるらしいよ！ #今日のプラベ',
        in_reply_to_id=status,
    )


parser = ArgumentParser()
parser.add_argument('time', type=int)
args = parser.parse_args()
count(args.time)
