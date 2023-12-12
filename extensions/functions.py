import discord
from discord.ext import commands
from datetime import datetime
from constants import GUILD_IKATODON_ID
from constants import CHANNEL_LOG_ID
from daug.utils.dpyexcept import excepter


def any_in(list: list, elements: list):
    return any(e in list for e in elements)


async def sleep(message: discord.Message):
    afk = message.guild.afk_channel
    vc = message.author.voice.channel
    if not afk:
        return await message.channel.send(f'{message.author.mention} おふとんはどこ？')
    if not vc:
        return await message.channel.send(f'{message.author.mention} ボイスチャンネルに入ってね！')
    for member in vc.members:
        await member.move_to(afk)
    await message.channel.send('おやすみなさい！')


class Functions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_ready(self):
        await self.bot.get_channel(CHANNEL_LOG_ID).send(str(datetime.now()))

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content:
            return
        if message.guild.id != GUILD_IKATODON_ID:
            return
        if str(self.bot.user.id) not in message.content:
            return
        if any_in(message.content, ['ふとん', '布団']):
            await sleep(message)
            return
        if any_in(message.content, ['黒歴史']):
            logs = [log async for log in message.channel.history() if log.author == message.author]
            await message.channel.delete_messages(logs)
            await message.channel.send(f'{message.author.mention} は何も言ってない、いいね？')
            return
        if any_in(message.content, ['バルス']):
            logs = [log async for log in message.channel.history() if log.author.bot]
            await message.channel.delete_messages(logs)
            await message.channel.send(f'{message.author.mention} botなんていなかった！')
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Functions(bot))
