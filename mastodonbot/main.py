import os
from mastodon import Mastodon

fedibird = Mastodon(
    access_token=os.getenv('MASTODON_TOKEN'),
    api_base_url='https://fedibird.com',
)
mentions = ' '.join([f'@{follower.acct}' for follower in fedibird.account_followers(77150)])
poll = fedibird.make_poll(
    options=('21時から参加可能', '22時から参加可能', '23時から参加可能', '行けたら行く'),
    expires_in=10000
)
fedibird.status_post(
    status=f'{mentions}\n #今日のプラベ 如何ですか？',
    poll=poll,
    visibility='private',
)
