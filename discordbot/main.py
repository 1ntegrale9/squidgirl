import os
from discord.ext import commands

if __name__ == '__main__':
    bot = commands.Bot(command_prefix=commands.when_mentioned_or(['.']))
    bot.id_user_kumasan = 358698798266056707
    bot.id_guild_ikatodon = 421485150984208386
    bot.id_category_emergency = 431454757626970113
    bot.id_channel_system = 475642109370826773
    bot.load_extension('cogs.general')
    bot.load_extension('cogs.emergency')
    bot.load_extension('cogs.database')
    bot.load_extension('jishaku')
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
