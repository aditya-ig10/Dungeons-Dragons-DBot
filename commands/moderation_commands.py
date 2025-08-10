# commands/moderation_commands.py
import logging
from discord.ext import commands
import discord
from discord import app_commands
import asyncio

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_mute_role(self, guild):
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
        return mute_role

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="User to ban", reason="Reason (optional)")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"Banned {member} for: {reason or 'No reason provided'}.")
        except Exception as e:
            logging.error(e)
            await interaction.response.send_message("Failed to ban user.", ephemeral=True)

    @app_commands.command(name="mute", description="Temporarily mute a user")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="User to mute", minutes="Duration in minutes")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        mute_role = await self.get_mute_role(interaction.guild)
        try:
            await member.add_roles(mute_role)
            await interaction.response.send_message(f"Muted {member} for {minutes} minutes.")
            await asyncio.sleep(minutes * 60)
            await member.remove_roles(mute_role)
        except Exception as e:
            logging.error(e)
            await interaction.response.send_message("Failed to mute user.", ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="User to unmute")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        mute_role = await self.get_mute_role(interaction.guild)
        try:
            await member.remove_roles(mute_role)
            await interaction.response.send_message(f"Unmuted {member}.")
        except Exception as e:
            logging.error(e)
            await interaction.response.send_message("Failed to unmute user.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))