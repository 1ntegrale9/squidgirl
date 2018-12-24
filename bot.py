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
            if message.content == '/raise':
                raise Exception
            if str(client.user.id) in message.content:
                args = message.content.split()
                if len(args) == 3 and str(client.user.id) in args[0] and args[1] == '教えて':
                    key = f'{message.guild.id}:{args[2]}'
                    if r.exists(key):
                        return f'{args[2]} は {r.get(key).decode()} だよ！'
                    else:
                        return 'それは知らないよ！'
                elif len(args) == 4 and str(client.user.id) in args[0] and args[1] == '覚えて':
                    key = f'{message.guild.id}:{args[2]}'
                    r.set(key, args[3])
                    r.sadd(str(message.guild.id), args[2])
                    return f'{args[2]} は {args[3]}、覚えた！'
                elif anyIn(message.content, ['ふとん', '布団']):
                    msg = await sleep(client, message)
                elif anyIn(message.content, ['黒歴史']):
                    logs = [log async for log in message.channel.history() if log.author == message.author]
                    await message.channel.delete_messages(logs)
                    msg = 'は何も言ってない、いいね？'
                elif anyIn(message.content, ['バルス']):
                    logs = [log async for log in message.channel.history() if log.author.bot]
                    await message.channel.delete_messages(logs)
                    msg = 'botなんていなかった！'
                else:
                    msg = random.choice(squidgirl_reply)
                mention = str(message.author.mention) + ' '
                await message.channel.send(mention + msg)
    except Exception as e:
        ch_error = client.get_channel(502906713545113642)
        await message.channel.send(str(e) + '\nっていうエラーが出たよ')
        await ch_error.send(f'```\n{traceback.format_exc()}\n```')


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


client.run(os.environ['DISCORD_BOT_TOKEN'])
