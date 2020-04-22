import discord
import os
import traceback
import redis
import random
from utils import anyIn
from discord.ext import commands
from datetime import datetime

bot = commands.Bot(command_prefix=('<@462797520007987201> ', '<@!462797520007987201> '))
r = redis.from_url(os.environ['REDIS_URL'])

ID_GUILD_IKATODON = 421485150984208386
ID_CATEGORY_EMERGENCY = 431454757626970113
ID_CHANNEL_LOGIN = 502837677108887582
ID_CHANNEL_ERROR = 502906713545113642
ID_USER_KUMASAN = 358698798266056707

splatoon_wiki = 'https://mntone.minibird.jp/splw/%E3%83%A1%E3%82%A4%E3%83%B3%E3%83%9A%E3%83%BC%E3%82%B8'

@bot.event
async def on_ready():
    await bot.get_channel(ID_CHANNEL_LOGIN).send(str(datetime.now()))

@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        await parse_message(message)
        await bot.process_commands(message)
    except Exception as e:
        ch_error = bot.get_channel(ID_CHANNEL_ERROR)
        await message.channel.send(str(e) + '\nっていうエラーが出たよ')
        await ch_error.send(f'```\n{traceback.format_exc()}\n```')


async def parse_message(message):
    if message.guild.id != ID_GUILD_IKATODON:
        return
    if message.channel.category_id == ID_CATEGORY_EMERGENCY:
        await emergency(message)
    if str(bot.user.id) not in message.content:
        return
    args = message.content.split()
    if len(args) in [3, 4]:
        return await database(message, args)
    if anyIn(message.content, ['ふとん', '布団']):
        return await sleep(bot, message)
    if anyIn(message.content, ['黒歴史']):
        logs = [log async for log in message.channel.history() if log.author == message.author]
        await message.channel.delete_messages(logs)
        return await message.channel.send(f'{message.author.mention} は何も言ってない、いいね？')
    if anyIn(message.content, ['バルス']):
        logs = [log async for log in message.channel.history() if log.author.bot]
        await message.channel.delete_messages(logs)
        return await message.channel.send(f'{message.author.mention} botなんていなかった！')
    await message.channel.send(f'{message.author.mention} + なーに？')


async def emergency(message):
    if message.content[0] in ('「', '['):
        await rename(message)


async def rename(message):
    vc = message.author.voice.channel
    if not vc:
        return await message.channel.send(f'{message.author.mention} ボイスチャンネルに入ってね！')
    oldname = vc.name
    newname = message.content[1:]
    await vc.edit(name=newname)
    await message.channel.edit(name=newname)
    await message.channel.send(f'チャンネル名を {oldname} から {newname} に変更したよ！')


async def database(message, args):
    if str(bot.user.id) not in args[0]:
        return
    if len(args) == 3:
        await oshiete(message, args)
        return
    if len(args) == 4:
        await oboete(message, args)


async def oshiete(message, args):
    if args[1] != '教えて':
        return
    key = f'{message.guild.id}:{args[2]}'
    if r.exists(key):
        msg = f'{args[2]} は {list(r.smembers(key))[0].decode()} だよ！'
    else:
        msg = 'それは知らないよ！'
    await message.channel.send(f'{message.author.mention} {msg}')


async def oboete(message, args):
    if args[1] != '覚えて':
        return
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
    await message.channel.send(f'{message.author.mention} {msg}')


async def sleep(client, message):
    afk = message.guild.afk_channel
    vc = message.author.voice.channel
    if not afk:
        return await message.channel.send(f'{message.author.mention} おふとんはどこ？')
    if not vc:
        return await message.channel.send(f'{message.author.mention} ボイスチャンネルに入ってね！')
    for member in vc.members:
        await member.move_to(afk)
    await message.channel.send('おやすみなさい！')


bot.load_extension('jishaku')
bot.run(os.environ['DISCORD_BOT_TOKEN'])
