import discord
from discord.ext import commands
from constants import TOKEN

extensions = (
    'auto_room',
    'functions',
    'instant_room',
)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix=commands.when_mentioned_or('$ '),
            help_command=None,
        )

    async def setup_hook(self):
        for extension in extensions:
            await self.load_extension(f'extensions.{extension}')
        await self.tree.sync()


def main():
    MyBot().run(TOKEN)


if __name__ == '__main__':
    main()
