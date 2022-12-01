from discord.ext import commands
from datetime import datetime
import traceback


def anyin(list, elements):
    return any(e in list for e in elements)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.get_channel(self.bot.id_channel_system).send(str(datetime.now()))

    async def perse(self, message):
        if message.guild.id != self.bot.id_guild_splatoon:
            return
        if str(self.bot.user.id) not in message.content:
            return
        if anyin(message.content, ['ふとん', '布団']):
            return await self.sleep(self.bot, message)
        if anyin(message.content, ['黒歴史']):
            logs = [log async for log in message.channel.history() if log.author == message.author]
            await message.channel.delete_messages(logs)
            return await message.channel.send(f'{message.author.mention} は何も言ってない、いいね？')
        if anyin(message.content, ['バルス']):
            logs = [log async for log in message.channel.history() if log.author.bot]
            await message.channel.delete_messages(logs)
            return await message.channel.send(f'{message.author.mention} botなんていなかった！')

    async def sleep(self, message):
        afk = message.guild.afk_channel
        vc = message.author.voice.channel
        if not afk:
            return await message.channel.send(f'{message.author.mention} おふとんはどこ？')
        if not vc:
            return await message.channel.send(f'{message.author.mention} ボイスチャンネルに入ってね！')
        for member in vc.members:
            await member.move_to(afk)
        await message.channel.send('おやすみなさい！')

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
            if not message.content:
                return
            if message.guild.id != self.bot.id_guild_splatoon:
                return
            await self.perse(message)
        except Exception as e:
            await message.channel.send(str(e) + '\nっていうエラーが出たよ')
            await self.bot.get_channel(self.bot.id_channel_system).send(
                f'```\n{traceback.format_exc()}\n```'
            )


def setup(bot):
    bot.add_cog(General(bot))
