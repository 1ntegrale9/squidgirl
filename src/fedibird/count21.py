import os
from mastodon import Mastodon

fedibird = Mastodon(
    access_token=os.getenv('MASTODON_TOKEN'),
    api_base_url='https://fedibird.com',
)

statuses = sorted(
    fedibird.account_statuses(77150),
    key=lambda status: status['created_at'],
    reverse=True,
)
status_poll = [status['poll'] for status in statuses if status['poll'] is not None][0]
votes = [poll['votes_count'] for poll in status_poll['options'] if poll['title'] == '21時から参加可能'][0]

fedibird.status_reply(
    to_status=status_poll,
    status=f'21時から{votes}人が参加できるらしいよ！ #今日のプラベ'
)
