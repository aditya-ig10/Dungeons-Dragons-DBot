# commands/notes_commands.py
import logging
from discord.ext import commands
import discord
from discord import app_commands
from utils.data_manager import *

class CampaignCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="note", description="Add campaign note with timestamp")
    @app_commands.describe(text="Note text")
    async def note(self, interaction: discord.Interaction, text: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        add_note(interaction.guild_id, text)
        await interaction.response.send_message("Note added.")

    @app_commands.command(name="notes", description="View all campaign notes (paginated)")
    async def notes(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        notes = get_notes(interaction.guild_id)
        if not notes:
            await interaction.response.send_message("No notes.")
            return
        embed = discord.Embed(title="Campaign Notes", color=discord.Color.dark_blue())
        for n in notes[-10:]:  # Simple pagination: last 10
            embed.add_field(name=n['time'], value=n['note'], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quest", description="Add/update quest with status")
    @app_commands.describe(name="Quest name", desc="Description", status="active/completed/failed/on_hold")
    async def quest(self, interaction: discord.Interaction, name: str, desc: str, status: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if status not in ['active', 'completed', 'failed', 'on_hold']:
            await interaction.response.send_message("Invalid status.", ephemeral=True)
            return
        add_or_update_quest(interaction.guild_id, name, desc, status)
        await interaction.response.send_message(f"Quest {name} set to {status}.")

    @app_commands.command(name="quests", description="View all quests grouped by status")
    async def quests(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        quests = get_quests(interaction.guild_id)
        embed = discord.Embed(title="Quests", color=discord.Color.gold())
        for st, qlist in quests.items():
            if qlist:
                value = "\n".join(f"{q['name']}: {q['desc']}" for q in qlist)
                embed.add_field(name=st.capitalize(), value=value, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="location", description="Set or view party location")
    @app_commands.describe(loc="New location (leave blank to view)")
    async def location(self, interaction: discord.Interaction, loc: str = None):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if loc:
            set_location(interaction.guild_id, loc)
            await interaction.response.send_message(f"Location set to {loc}.")
        else:
            current = get_location(interaction.guild_id)
            await interaction.response.send_message(f"Current location: {current or 'Unknown'}.")

    @app_commands.command(name="session", description="Start new session and join voice channel")
    async def session(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message("You must be in a voice channel to start a session.", ephemeral=True)
            return
        channel = user.voice.channel
        perms = channel.permissions_for(interaction.guild.me)
        if not perms.connect or not perms.speak:
            await interaction.response.send_message("I don't have permission to join or speak in that voice channel.", ephemeral=True)
            return
        try:
            await channel.connect()
            set_session_voice(interaction.guild_id, channel.id)
            await interaction.response.send_message(f"Session started. Joined {channel.name}.")
        except Exception as e:
            logging.error(e)
            await interaction.response.send_message("Failed to join voice channel.", ephemeral=True)

    @app_commands.command(name="leave", description="End session and leave voice channel")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            set_session_voice(interaction.guild_id, None)
            await interaction.response.send_message("Session ended. Left voice channel.")
        else:
            await interaction.response.send_message("Not currently in a voice channel.", ephemeral=True)

    @app_commands.command(name="inventory", description="Add items to party inventory")
    @app_commands.describe(item="Item name", qty="Quantity", desc="Description")
    async def inventory(self, interaction: discord.Interaction, item: str, qty: int, desc: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        add_inventory(interaction.guild_id, item, qty, desc)
        await interaction.response.send_message(f"Added {qty} x {item} to inventory.")

    @app_commands.command(name="bag", description="View party inventory with descriptions")
    async def bag(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        inv = get_inventory(interaction.guild_id)
        if not inv:
            await interaction.response.send_message("Inventory is empty.")
            return
        embed = discord.Embed(title="Party Inventory", color=discord.Color.teal())
        for item, data in inv.items():
            embed.add_field(name=item, value=f"Quantity: {data['qty']}\nDescription: {data['desc']}", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CampaignCog(bot))