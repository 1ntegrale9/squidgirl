import discord
import os
import traceback
import redis
import random
import datetime
from scrapbox_client import getDescriptions
from utils import anyIn
from discord.ext import tasks, commands
from mastodon import Mastodon

bot = commands.Bot(command_prefix='!')
r = redis.from_url(os.environ['REDIS_URL'])

isNoticed = False
fedibird = Mastodon(
    access_token=os.getenv('MASTODON_TOKEN'),
    api_base_url='https://fedibird.com',
)

ID_GUILD_IKATODON = 421485150984208386
ID_CATEGORY_EMERGENCY = 431454757626970113
ID_CHANNEL_LOGIN = 502906433914798093
ID_CHANNEL_ERROR = 502906713545113642
ID_USER_KUMASAN = 358698798266056707


@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        await parse_message(message)
    except Exception as e:
        ch_error = bot.get_channel(ID_CHANNEL_ERROR)
        await message.channel.send(str(e) + '\nっていうエラーが出たよ')
        await ch_error.send(f'```\n{traceback.format_exc()}\n```')


async def parse_message(message):
    if message.content == '/raise':
        raise Exception
    if message.content == '/connect':
        await bot.get_channel(574595949603848212).connect()
    if message.content == '/play':
        bot.voice_clients[0].play(discord.FFmpegPCMAudio('test.wav'))
    if message.content == '/disconnect':
        await bot.voice_clients[0].disconnect()
    if str(bot.user.id) in message.content:
        args = message.content.split()
        if len(args) == 3 and str(bot.user.id) in args[0] and args[1] == '教えて':
            key = f'{message.guild.id}:{args[2]}'
            if r.exists(key):
                msg = f'{args[2]} は {list(r.smembers(key))[0].decode()} だよ！'
            else:
                msg = 'それは知らないよ！'
        elif len(args) == 4 and str(bot.user.id) in args[0] and args[1] == '覚えて':
            key = f'{message.guild.id}:{args[2]}'
            if r.exists(key):
                old = list(r.smembers(key))[0].decode()
                r.sadd(key, args[3])
                r.sadd(str(message.guild.id), args[2])
                msg = f'{args[2]} は {old} じゃなかったっけ？\n{args[3]} で覚え直したよ！'
            else:
                r.sadd(key, args[3])
                r.sadd(str(message.guild.id), args[2])
                msg = f'{args[2]} は {args[3]}、覚えた！'
        elif anyIn(message.content, ['ふとん', '布団']):
            msg = await sleep(bot, message)
        elif anyIn(message.content, ['黒歴史']):
            logs = [log async for log in message.channel.history() if log.author == message.author]
            await message.channel.delete_messages(logs)
            msg = 'は何も言ってない、いいね？'
        elif anyIn(message.content, ['バルス']):
            logs = [log async for log in message.channel.history() if log.author.bot]
            await message.channel.delete_messages(logs)
            msg = 'botなんていなかった！'
        else:
            msg = random.choice(getDescriptions('squidgirl', 'reply'))
        mention = str(message.author.mention) + ' '
        await message.channel.send(mention + msg)


async def on_member_update(before, after):
    if before.id == ID_USER_KUMASAN:
        target_channel = bot.get_channel(ID_CATEGORY_EMERGENCY)
        target_role = bot.get_guild(ID_GUILD_IKATODON).default_role
        if after.status is discord.Status.offline:
            await target_channel.set_permissions(target_role, read_messages=True)
        elif after.status is discord.Status.online:
            await target_channel.set_permissions(target_role, read_messages=False)


async def sleep(client, message):
    afk = message.guild.afk_channel
    vc = message.author.voice.channel
    if not afk:
        return 'おふとんはどこ？'
    if not vc:
        return 'ボイスチャンネルに入ってね！'
    mentions = ''
    for member in vc.members:
        await member.move_to(afk)
        if member != message.author:
            mentions = mentions + member.mention + ' '
    return f'{mentions}\nおやすみなさい！'


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
bot.run(os.environ['DISCORD_BOT_TOKEN'])
