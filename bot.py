import discord
import os
import traceback

client = discord.Client()


@client.event
async def send2developer(msg):
    developer = client.get_user(314387921757143040)
    dm = await developer.create_dm()
    await dm.send(msg)


@client.event
async def on_ready():
    msg = f'Logged on as {client.user}!'
    await send2developer(msg)


@client.event
async def on_message(message):
    try:
        if message.author != client.user:
            msg = 'Message from {0.author}: {0.content}'.format(message)
            await send2developer(msg)
    except Exception:
        await send2developer(traceback.format_exc())


client.run(os.environ['DISCORD_BOT_TOKEN'])
