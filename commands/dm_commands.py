# commands/dm_commands.py
from discord.ext import commands
import discord
from discord import app_commands
from utils.dice_parser import parse_and_roll
from utils.data_manager import *

class DMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dmhp", description="Set character HP directly")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(name="Character name", hp="New HP value")
    async def dmhp(self, interaction: discord.Interaction, name: str, hp: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        update_hp(interaction.guild_id, name, hp)
        await interaction.response.send_message(f"Set {name}'s HP to {hp}.")

    @app_commands.command(name="damage", description="Deal damage to a character")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(name="Character name", amount="Damage amount")
    async def damage(self, interaction: discord.Interaction, name: str, amount: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        damage_character(interaction.guild_id, name, amount)
        char = get_character(interaction.guild_id, name)
        await interaction.response.send_message(f"Dealt {amount} damage to {name}. Current HP: {char['hp']}/{char['max_hp']}.")

    @app_commands.command(name="heal", description="Heal a character")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(name="Character name", amount="Heal amount")
    async def heal(self, interaction: discord.Interaction, name: str, amount: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        heal_character(interaction.guild_id, name, amount)
        char = get_character(interaction.guild_id, name)
        await interaction.response.send_message(f"Healed {name} by {amount}. Current HP: {char['hp']}/{char['max_hp']}.")

    @app_commands.command(name="attack", description="NPC attack with damage calculations")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(target="Target character", bonus="Attack bonus", damage="Damage dice notation")
    async def attack(self, interaction: discord.Interaction, target: str, bonus: int, damage: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        try:
            to_hit, _ = parse_and_roll(f"1d20 + {bonus}")
            dmg, dmg_details = parse_and_roll(damage)
            embed = discord.Embed(title="NPC Attack", color=discord.Color.red())
            embed.add_field(name="To Hit", value=to_hit, inline=False)
            embed.add_field(name="Potential Damage", value=dmg, inline=False)
            for det in dmg_details:
                rolls_str = f"Rolls: {det['rolls']}"
                if det['kept'] != det['rolls']:
                    rolls_str += f"\nKept: {det['kept']}"
                embed.add_field(name=det['expression'], value=rolls_str, inline=True)
            await interaction.response.send_message(embed=embed)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

    @app_commands.command(name="status", description="View all character status overview")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def status(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        chars = get_all_characters(interaction.guild_id)
        if not chars:
            await interaction.response.send_message("No characters added.")
            return
        embed = discord.Embed(title="Character Status Overview", color=discord.Color.orange())
        for name, data in chars.items():
            embed.add_field(name=name, value=f"HP: {data['hp']}/{data['max_hp']}", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DMCog(bot))