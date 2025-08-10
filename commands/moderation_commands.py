"""
Moderation commands: ban, mute, unmute
"""
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

async def setup_moderation_commands(bot):
    """Setup moderation commands"""
    
    @bot.tree.command(name='ban', description='Ban a user from the server')
    @app_commands.describe(
        user='User to ban',
        reason='Reason for the ban (optional)'
    )
    async def ban_user(interaction: discord.Interaction, user: discord.Member, reason: str = None):
        """Ban user command"""
        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to ban members",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Bot Permission Error",
                description="I don't have permission to ban members",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Check role hierarchy
        if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description="You can't ban someone with equal or higher role",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Send DM to user (optional)
            try:
                dm_embed = discord.Embed(
                    title="🔨 You have been banned",
                    description=f"You have been banned from {interaction.guild.name}",
                    color=0xff0000
                )
                if reason:
                    dm_embed.add_field(name="Reason", value=reason, inline=False)
                await user.send(embed=dm_embed)
            except:
                pass  # Ignore if can't send DM
            
            # Ban the user
            await user.ban(reason=reason, delete_message_days=0)
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔨 User Banned",
                color=0xff0000
            )
            embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to ban this user",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name='mute', description='Mute a user for specified minutes')
    @app_commands.describe(
        user='User to mute',
        minutes='Duration in minutes',
        reason='Reason for the mute (optional)'
    )
    async def mute_user(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = None):
        """Mute user command"""
        # Check permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to moderate members",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Bot Permission Error",
                description="I don't have permission to moderate members",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check role hierarchy
        if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description="You can't mute someone with equal or higher role",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate minutes
        if minutes <= 0 or minutes > 40320:  # 28 days max
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Duration must be between 1 and 40320 minutes (28 days)",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Calculate timeout duration
            until = datetime.now() + timedelta(minutes=minutes)
            
            # Apply timeout
            await user.timeout(until, reason=reason)
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔇 User Muted",
                color=0xff9500
            )
            embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)
            embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Expires", value=f"<t:{int(until.timestamp())}:R>", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to mute this user",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name='unmute', description='Unmute a user')
    @app_commands.describe(user='User to unmute')
    async def unmute_user(interaction: discord.Interaction, user: discord.Member):
        """Unmute user command"""
        # Check permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to moderate members",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user is actually muted
        if not user.timed_out_until:
            embed = discord.Embed(
                title="❌ User Not Muted",
                description="This user is not currently muted",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Remove timeout
            await user.timeout(None)
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔊 User Unmuted",
                color=0x00ff00
            )
            embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unmute this user",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
