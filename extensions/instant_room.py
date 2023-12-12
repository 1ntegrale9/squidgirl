import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from daug.utils import get_related_tc
from daug.utils import get_related_vc
from constants import GUILD_IKATODON_ID
from constants import CATEGORY_EMERGENCY_ID
from daug.utils.dpyexcept import excepter


async def rename(message: discord.Message):
    vc = message.author.voice and message.author.voice.channel
    if vc is None or vc.category_id != CATEGORY_EMERGENCY_ID:
        return
    if message.content[0] in ('「', '['):
        if len(message.content) < 2:
            return
    oldname = vc.name
    newname = message.content[1:]
    if isinstance(message.channel, discord.channel.TextChannel):
        tc = message.channel
        vc = get_related_vc(message.channel)
    if isinstance(message.channel, discord.channel.VoiceChannel):
        tc = get_related_tc(message.channel)
        vc = message.channel
    await vc.edit(name=newname)
    await tc.edit(name=newname)
    await message.channel.send(f'チャンネル名を {oldname} から {newname} に変更したよ！')


async def create_vc(interaction, category: discord.CategoryChannel):
    name = interaction.user.display_name + 'の部屋'
    vc = await category.create_voice_channel(name=name)
    tc = await category.create_text_channel(name=name, topic=str(vc.id))
    await tc.send(view=ChannelFunctionButtons())
    await vc.send(f'{interaction.user.mention} お部屋の用意ができたよ！\n部屋に誰もいなくなった時か、1時間に1回の無人確認で部屋を消していくよ', view=ChannelFunctionButtons())


class ChannelFunctionButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='部屋名変更', emoji='🔧', row=0, style=discord.ButtonStyle.blurple, custom_id='instant_room:channel_function:rename')
    @excepter
    async def _rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.channel
        if isinstance(interaction.channel, discord.channel.TextChannel):
            vc = get_related_vc(interaction.channel)
        if vc is None or interaction.user not in vc.members:
            await interaction.response.send_message('部屋に入ってから操作してね', ephemeral=True)
            return
        await interaction.response.send_modal(EditRoomNameModal())

    @discord.ui.button(label='人数変更', emoji='🔧', row=1, style=discord.ButtonStyle.blurple, custom_id='instant_room:channel_function:edit_user_limit')
    @excepter
    async def _edit_user_limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.channel
        if isinstance(interaction.channel, discord.channel.TextChannel):
            vc = get_related_vc(interaction.channel)
        if vc is None or interaction.user not in vc.members:
            await interaction.response.send_message('部屋に入ってから操作してね', ephemeral=True)
            return
        await interaction.response.send_modal(EditUserLimitModal())


class CreateVoiceChannelButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='りんじ部屋を作る', style=discord.ButtonStyle.green, custom_id='instant_room:create_room')
    @excepter
    async def _create_voice_channel_group_chat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        category = interaction.guild.get_channel(CATEGORY_EMERGENCY_ID)
        await interaction.response.send_message(f'{category.name} に部屋を用意するね', ephemeral=True)
        await create_vc(interaction, category)


class EditRoomNameModal(discord.ui.Modal, title='部屋名を変更する'):
    def __init__(self):
        super().__init__()

    name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label='新しい部屋の名前',
        required=True,
    )

    @excepter
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        if isinstance(interaction.channel, discord.channel.TextChannel):
            await interaction.response.defer(ephemeral=False)
            tc = interaction.channel
            vc = get_related_vc(interaction.channel)
        if isinstance(interaction.channel, discord.channel.VoiceChannel):
            await interaction.response.defer(ephemeral=True)
            tc = get_related_tc(interaction.channel)
            vc = interaction.channel
        await vc.edit(name=name)
        await tc.edit(name=name)
        message = f'{interaction.user.mention} 部屋名を {name} に変更したよ'
        if isinstance(interaction.channel, discord.channel.TextChannel):
            await interaction.followup.send(message)
        if isinstance(interaction.channel, discord.channel.VoiceChannel):
            await interaction.followup.send(message, ephemeral=True)
            await tc.send(message)


class EditUserLimitModal(discord.ui.Modal, title='人数上限を変更する'):
    def __init__(self):
        super().__init__()

    user_limit = discord.ui.TextInput(
        placeholder='0で人数上限をなしにします',
        style=discord.TextStyle.short,
        label='人数上限（数字）',
        required=True,
    )

    @excepter
    async def on_submit(self, interaction: discord.Interaction):
        user_limit = self.user_limit.value
        if not user_limit.isdecimal():
            await interaction.followup.send('0~99の数値を入力してね', ephemeral=True)
            return
        user_limit = int(user_limit)
        if isinstance(interaction.channel, discord.channel.TextChannel):
            await interaction.response.defer(ephemeral=False)
            tc = interaction.channel
            vc = get_related_vc(interaction.channel)
        if isinstance(interaction.channel, discord.channel.VoiceChannel):
            await interaction.response.defer(ephemeral=True)
            tc = get_related_tc(interaction.channel)
            vc = interaction.channel
        await vc.edit(user_limit=user_limit)
        message = f'{interaction.user.mention} 人数上限を {user_limit} 人に変更したよ'
        if isinstance(interaction.channel, discord.channel.TextChannel):
            await interaction.followup.send(message, ephemeral=False)
        if isinstance(interaction.channel, discord.channel.VoiceChannel):
            await interaction.followup.send(message, ephemeral=True)
            await tc.send(message)


class InstantRoomCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(CreateVoiceChannelButton())
        self.bot.add_view(ChannelFunctionButtons())
        self.deleter.start()

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild.id != GUILD_IKATODON_ID:
            return
        if message.channel.category_id != CATEGORY_EMERGENCY_ID:
            return
        await rename(message)
        if self.bot.user.mention in message.content or message.content in ['め', 'メ', 'メニュー', 'ボタン', 'ボタンメニュー']:
            if message.channel.category_id == CATEGORY_EMERGENCY_ID:
                await message.channel.send(view=ChannelFunctionButtons())
                return

    @app_commands.command(name='りんじ部屋作成ボタン', description='りんじ部屋作成ボタンを設置します')
    @app_commands.guild_only()
    @excepter
    async def _room_factory_panel_command(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.manage_channels:
            await interaction.response.send_message('管理者専用機能です', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        channel = self.bot.get_channel(1184205030979555508)
        await channel.send(view=CreateVoiceChannelButton())
        await interaction.followup.send(f'{channel.mention} に操作パネルを設置したよ', ephemeral=True)

    @commands.Cog.listener()
    @excepter
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        if member.bot:
            return
        bch, ach = before.channel, after.channel
        if bch and ach and bch.id == ach.id:
            return
        if bch and bch.category_id == CATEGORY_EMERGENCY_ID and len(bch.members) == 0:
            try:
                tc = get_related_tc(bch)
                await bch.delete()
                await tc.delete()
            except discord.errors.NotFound:
                pass

    @tasks.loop(hours=1.0)
    @excepter
    async def deleter(self):
        category = self.bot.get_channel(CATEGORY_EMERGENCY_ID)
        for channel in category.voice_channels:
            if len(channel.members) > 0:
                continue
            tc = get_related_tc(channel)
            await channel.delete()
            await tc.delete()

    @deleter.before_loop
    async def before_deleter(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InstantRoomCog(bot))
