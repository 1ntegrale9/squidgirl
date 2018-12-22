import discord
import os
import traceback
import redis
import random
from scrapbox_client import getDescriptions
from utils import anyIn

client = discord.Client()
r = redis.from_url(os.environ['REDIS_URL'])

squidgirl_reply = getDescriptions('squidgirl', 'reply')


@client.event
async def on_ready():
    ch_login = client.get_channel(502906433914798093)
    await ch_login.send('ログインしました')


@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        else:
            await logging(client, message)
            if message.content == '/raise':
                raise Exception
            if str(client.user.id) in message.content:
                if anyIn(message.content, ['ふとん, 布団']):
                    msg = await sleep(client, message)
                elif anyIn(message.content, ['黒歴史']):
                    async for log in message.channel.history:
                        if log.author == message.author:
                            await log.delete()
                    msg = 'は何も言ってない、いいね？'
                elif anyIn(message.content, ['バルス']):
                    async for log in message.channel.history:
                        if log.author.bot:
                            await log.delete()
                    msg = 'botなんていなかった！'
                elif message.content.startswith(f'<@{client.user.id}>'):
                    msg = await knowledge(client, message)
                else:
                    msg = random.choice(squidgirl_reply)
                mention = str(message.author.mention) + ' '
                await message.channel.send(mention + msg)
    except Exception as e:
        ch_error = client.get_channel(502906713545113642)
        await message.channel.send(str(e) + '\nっていうエラーが出たよ')
        await ch_error.send(f'```\n{traceback.format_exc()}\n```')


async def logging(client, message):
    ch_log = client.get_channel(525940371042205706)
    msg = 'Message from {0.author}: {0.content}'.format(message)
    await ch_log.send(msg)


async def sleep(client, message):
    compatible_channel = [
        c for c in message.guild.channels
        if message.channel.name.upper() in c.name]
    if compatible_channel:
        compatible_channel = compatible_channel[0]
        channel_voice_members = discord.utils.get(
            message.guild.channels,
            name=compatible_channel.name,
            type=discord.ChannelType.voice
        ).voice_members
        for member in channel_voice_members:
            await member.move_to(message.guild.afk_channel)
        return 'おやすみなさい、良い夢を'
    else:
        return 'ボイスチャンネルが見つからないよ！'


async def knowledge(client, message):
    args = message.content.split()
    if len(args) == 3 and args[1] == '教えて':
        key = f'{message.guild.id}:{args[2]}'
        if r.exists(key):
            return f'{args[2]} は {r.get(key).decode()} だよ！'
        else:
            return '？'
    elif len(args) == 4 and args[1] == '覚えて':
        key = f'{message.guild.id}:{args[2]}'
        r.set(key, args[3])
        r.sadd(str(message.guild.id), args[2])
        return f'{args[2]} は {args[3]}、覚えた！'
    else:
        return random.choice(squidgirl_reply)


client.run(os.environ['DISCORD_BOT_TOKEN'])