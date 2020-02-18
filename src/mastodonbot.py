import os
import datetime
from discord.ext import tasks, commands
from mastodon import Mastodon

bot = commands.Bot(command_prefix='!')
isNoticed = False
fedibird = Mastodon(
    access_token=os.getenv('MASTODON_TOKEN'),
    api_base_url='https://fedibird.com',
)


@tasks.loop(seconds=60)
async def today_private_match():
    global isNoticed
    if isNoticed or (20 != datetime.datetime.now().hour):
        return
    mentions = ' '.join([f'@{follower.acct}' for follower in fedibird.account_followers(77150)])
    poll = fedibird.make_poll(
        options=['21時から参加可能', '22時から参加可能', '23時から参加可能', '行けたら行く'],
        expires_in=10000
    )
    fedibird.status_post(
        status=f'{mentions} #今日のプラベ 如何ですか？',
        poll=poll
    )
    isNoticed = True


@today_private_match.before_loop
async def before_loop():
    await bot.wait_until_ready()


today_private_match.start()
