import discord
from discord import app_commands
from discord.ext import commands
from daug.utils.dpyexcept import excepter
from dataclasses import dataclass

MAX_STRING_LENGTH = 7
CATEGORY_EMERGENCY2_ID = 1184208390289891358
CAHHENL_EMERGENCY_FACTORY_ID = 1184208530182504508


@dataclass
class MatchingFields():
    room_name: str = 'りんじ'
    room_count: str = 0
    user_limit: str = 3


def extract_channels(room_name: str, category: discord.CategoryChannel) -> list[discord.abc.GuildChannel]:
    return [ch for ch in category.channels if not is_room(room_name, ch)]


def extract_voice_channels(room_name: str, category: discord.CategoryChannel) -> list[discord.VoiceChannel]:
    return [vc for vc in category.voice_channels if not is_room(room_name, vc)]


def extract_rooms(room_name: str, category: discord.CategoryChannel) -> list[discord.VoiceChannel]:
    rooms = []
    for n in range(1, 50):
        for vc in category.voice_channels:
            if not vc.name.startswith(room_name):
                continue
            room_number = vc.name.split(room_name)[1]
            if not room_number.isdigit():
                continue
            if int(room_number) == n:
                rooms.append(vc)
    return rooms


def is_room(room_name: str, vc: discord.VoiceChannel):
    if not vc.name.startswith(room_name):
        return False
    if not vc.name.split(room_name)[1].isdigit():
        return False
    return True


def compose_embed(fields: MatchingFields = MatchingFields()) -> discord.Embed:
    embed = discord.Embed(description='現在の設定')
    embed.add_field(name='部屋名', value=fields.room_name)
    embed.add_field(name='部屋数', value=fields.room_count)
    embed.add_field(name='上限人数', value=fields.user_limit)
    return embed


def extract_embed_fields(embed: discord.Embed) -> MatchingFields:
    fields = MatchingFields()
    fields.room_name = [field.value for field in embed.fields if field.name == '部屋名'][0]
    fields.room_count = [field.value for field in embed.fields if field.name == '部屋数'][0]
    fields.user_limit = [field.value for field in embed.fields if field.name == '上限人数'][0]
    return fields


class PrepareRoomModal(discord.ui.Modal, title='部屋の用意と片付け'):
    def __init__(self, fields: MatchingFields):
        super().__init__()
        self.fields: MatchingFields = fields
        self.room_name = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label='カテゴリ内の部屋の名前',
            default=self.fields.room_name,
            required=True,
        )
        self.room_count = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label='カテゴリ内の部屋の数',
            default=self.fields.room_count,
            required=True,
        )
        self.user_limit = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label='各部屋の上限人数',
            default=self.fields.user_limit,
            required=True,
        )
        self.add_item(self.room_name)
        self.add_item(self.room_count)
        self.add_item(self.user_limit)

    @excepter
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        room_name = self.room_name.value
        if len(room_name) > MAX_STRING_LENGTH:
            await interaction.response.send_message(f'部屋名は{MAX_STRING_LENGTH}文字以内で指定してね', ephemeral=True)
            return

        channels = interaction.channel.category.channels
        voice_channels = interaction.channel.category.voice_channels
        rooms = {}
        for vc in voice_channels:
            if is_room(room_name, vc) and 1 <= int(vc.name.split(room_name)[1]) <= 50:
                if rooms.get(vc.name):
                    await vc.delete()
                rooms[vc.name] = vc
        max_room_count = 50 - len(channels) + len(rooms)

        count = self.room_count.value
        if not count.isdigit():
            await interaction.followup.send('部屋の数には整数を指定してね', ephemeral=True)
            return
        count = int(count)
        if count > max_room_count:
            await interaction.followup.send(f'部屋の数は {max_room_count} 以下で指定してね', ephemeral=True)
            return

        user_limit = self.user_limit.value
        if not user_limit.isdigit():
            await interaction.followup.send('部屋の数には整数を指定してね', ephemeral=True)
            return
        user_limit = int(user_limit)

        for n in range(1, 50):
            room: discord.VoiceChannel = rooms.get(f'{room_name}{n}')
            if n > count:
                if room:
                    await room.delete()
                continue
            if room:
                if room.user_limit != user_limit:
                    await room.edit(user_limit=user_limit)
                continue
            await interaction.channel.category.create_voice_channel(
                name=f'{room_name}{n}',
                user_limit=user_limit,
            )

        self.fields.room_name = self.room_name.value
        self.fields.room_count = self.room_count.value
        self.fields.user_limit = self.user_limit.value
        embed = compose_embed(self.fields)
        await interaction.message.edit(embed=embed)
        await interaction.followup.send('部屋の準備/片付けが完了したよ', ephemeral=True)


class OperationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='部屋の用意と片付け', style=discord.ButtonStyle.green, custom_id='auto_room:factory')
    @excepter
    async def _room_factory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        fields = extract_embed_fields(interaction.message.embeds[0])
        await interaction.response.send_modal(PrepareRoomModal(fields))


class AutoRoomCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(OperationButtons())

    @app_commands.command(name='りんじ部屋工場', description='りんじ部屋の操作パネルを設置します')
    @app_commands.guild_only()
    @excepter
    async def _room_factory_panel_command(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.manage_channels:
            await interaction.response.send_message('管理者専用機能です', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        channel = self.bot.get_channel(CAHHENL_EMERGENCY_FACTORY_ID)
        await channel.send(embed=compose_embed(), view=OperationButtons())
        await interaction.followup.send(f'{channel.mention} に操作パネルを設置したよ', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoRoomCog(bot))
