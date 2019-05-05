import discord
import os

client = discord.Client()
token = os.environ['DISCORD_BOT_TOKEN_SQUIDGIRL']

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == ('/voice'):
        voice = await client.get_channel(574595949603848212).connect()
        voice.play(discord.FFmpegPCMAudio('test.wav'))

client.run(token)
