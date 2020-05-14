from discord.ext import commands
import traceback


class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def optimize(self, ctx):
        if ctx.guild.id != self.bot.id_guild_ikatodon:
            return
        emergency = ctx.guild.get_channel(self.bot.id_category_emergency)
        for ch in emergency.voice_channels:
            if len(ch.members) > 0:
                return await ctx.send('まだ人がいるよ！')
        for ch in emergency.channels:
            await ch.delete()
        for i in range(1, 6, 1):
            await ctx.guild.create_text_channel(
                name=f'りんじ{i}',
                category=emergency
            )
            await ctx.guild.create_voice_channel(
                name=f'りんじ{i}',
                category=emergency
            )

    async def rename(self, message):
        vc = message.author.voice.channel
        if not vc:
            await message.channel.send(
                f'{message.author.mention} ボイスチャンネルに入ってね！'
            )
            return
        oldname = vc.name
        newname = message.content[1:]
        await vc.edit(name=newname)
        await message.channel.edit(name=newname)
        await message.channel.send(f'チャンネル名を {oldname} から {newname} に変更したよ！')

    async def perse(self, message):
        if message.channel.category_id != self.bot.id_category_emergency:
            return
        if message.content[0] in ('「', '['):
            if len(message.content) < 2:
                return
            await self.rename(message)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
            if not message.content:
                return
            if message.guild.id != self.bot.id_guild_ikatodon:
                return
            await self.perse(message)
        except Exception as e:
            await message.channel.send(str(e) + '\nっていうエラーが出たよ')
            await self.bot.get_channel(self.bot.id_channel_system).send(
                f'```\n{traceback.format_exc()}\n```'
            )


def setup(bot):
    bot.add_cog(Emergency(bot))
