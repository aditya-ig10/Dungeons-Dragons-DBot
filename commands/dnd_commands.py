# commands/dnd_commands.py
from discord.ext import commands
import discord
from discord import app_commands
from utils.dice_parser import parse_and_roll
from utils.data_manager import *

class DNDCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Advanced dice rolling with D&D notation")
    @app_commands.describe(notation="e.g., 2d6+3, 4d6kh3")
    async def roll(self, interaction: discord.Interaction, notation: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        try:
            total, details = parse_and_roll(notation)
            embed = discord.Embed(title="Dice Roll", color=discord.Color.blue())
            embed.add_field(name="Total", value=total, inline=False)
            for det in details:
                rolls_str = f"Rolls: {det['rolls']}"
                if det['kept'] != det['rolls']:
                    rolls_str += f"\nKept: {det['kept']}"
                embed.add_field(name=det['expression'], value=rolls_str, inline=True)
            await interaction.response.send_message(embed=embed)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

    @app_commands.command(name="initiative", description="Initiative tracking: add, view, clear")
    @app_commands.describe(action="add/view/clear", name="Character name (for add)", roll="Roll notation (for add)")
    async def initiative(self, interaction: discord.Interaction, action: str, name: str = None, roll: str = None):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild_id = interaction.guild_id
        if action.lower() == "add":
            if not name or not roll:
                await interaction.response.send_message("Provide name and roll notation.", ephemeral=True)
                return
            try:
                iroll, _ = parse_and_roll(roll)
                add_initiative(guild_id, name, iroll)
                await interaction.response.send_message(f"Added {name} with initiative {iroll}.")
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
        elif action.lower() == "view":
            init = get_initiative(guild_id)
            if not init:
                await interaction.response.send_message("No initiative order set.")
                return
            embed = discord.Embed(title="Initiative Order", color=discord.Color.green())
            for i, entry in enumerate(init, 1):
                embed.add_field(name=f"{i}. {entry['name']}", value=entry['roll'], inline=False)
            await interaction.response.send_message(embed=embed)
        elif action.lower() == "clear":
            clear_initiative(guild_id)
            await interaction.response.send_message("Initiative order cleared.")
        else:
            await interaction.response.send_message("Invalid action: use add, view, or clear.", ephemeral=True)

    @app_commands.command(name="addchar", description="Add a character with HP tracking")
    @app_commands.describe(name="Character name", max_hp="Maximum HP")
    async def addchar(self, interaction: discord.Interaction, name: str, max_hp: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        try:
            add_character(interaction.guild_id, name, max_hp)
            await interaction.response.send_message(f"Added character {name} with {max_hp} HP.")
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

    @app_commands.command(name="checkchar", description="View character details and status")
    @app_commands.describe(name="Character name")
    async def checkchar(self, interaction: discord.Interaction, name: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        char = get_character(interaction.guild_id, name)
        if not char:
            await interaction.response.send_message("Character not found.", ephemeral=True)
            return
        embed = discord.Embed(title=f"Character: {name}", color=discord.Color.purple())
        embed.add_field(name="HP", value=f"{char['hp']}/{char['max_hp']}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show bot help with feature categories")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="D&D Bot Help", description="Commands organized by category", color=discord.Color.green())
        embed.add_field(name="D&D Commands", value="/roll\n/initiative\n/addchar\n/checkchar", inline=False)
        embed.add_field(name="DM Commands (Require Manage Server)", value="/dmhp\n/damage\n/heal\n/attack\n/status", inline=False)
        embed.add_field(name="Campaign Management", value="/note\n/notes\n/quest\n/quests\n/location\n/session\n/leave\n/inventory\n/bag", inline=False)
        embed.add_field(name="Music Commands", value="/play\n/stop", inline=False)
        embed.add_field(name="Moderation Commands", value="/ban\n/mute\n/unmute", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DNDCog(bot))