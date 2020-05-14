from discord.ext import commands
import os
import traceback
import redis


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.r = redis.from_url(os.environ['REDIS_URL'])

    async def database(self, message, args):
        if str(self.bot.useself.r.id) not in args[0]:
            return
        if len(args) == 3:
            await self.oshiete(message, args)
            return
        if len(args) == 4:
            await self.oboete(message, args)

    async def oshiete(self, message, args):
        if args[1] != '教えて':
            return
        key = f'{message.guild.id}:{args[2]}'
        if self.self.r.exists(key):
            msg = f'{args[2]} は {list(self.r.smembers(key))[0].decode()} だよ！'
        else:
            msg = 'それは知らないよ！'
        await message.channel.send(f'{message.author.mention} {msg}')

    async def oboete(self, message, args):
        if args[1] != '覚えて':
            return
        key = f'{message.guild.id}:{args[2]}'
        if self.r.exists(key):
            old = list(self.r.smembers(key))[0].decode()
            self.r.sadd(key, args[3])
            self.r.sadd(str(message.guild.id), args[2])
            msg = f'{args[2]} は {old} じゃなかったっけ？\n{args[3]} で覚え直したよ！'
        else:
            self.r.sadd(key, args[3])
            self.r.sadd(str(message.guild.id), args[2])
            msg = f'{args[2]} は {args[3]}、覚えた！'
        await message.channel.send(f'{message.author.mention} {msg}')

    async def perse(self, message):
        args = message.content.split()
        if len(args) in [3, 4]:
            await self.database(message, args)

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
    bot.add_cog(Database(bot))
