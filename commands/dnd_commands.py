"""
D&D related commands: dice rolling, initiative tracking, character management
"""
import discord
from discord import app_commands
from discord.ext import commands
import re
from utils.dice_parser import DiceParser

async def setup_dnd_commands(bot):
    """Setup D&D commands"""
    
    @bot.tree.command(name='roll', description='Roll dice using D&D notation (e.g., 2d6+3)')
    @app_commands.describe(dice='Dice to roll (e.g., 1d20, 2d6+3, 4d6kh3)')
    async def roll_dice(interaction: discord.Interaction, dice: str):
        """Roll dice command"""
        try:
            parser = DiceParser()
            result = parser.parse_and_roll(dice)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                color=0xff6b6b
            )
            embed.add_field(name="Roll", value=f"`{dice}`", inline=True)
            embed.add_field(name="Result", value=f"**{result['total']}**", inline=True)
            
            if result['details']:
                embed.add_field(name="Details", value=result['details'], inline=False)
            
            embed.set_footer(text=f"Rolled by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Invalid Dice Roll",
                description=f"Error: {str(e)}\n\nExamples:\n• `1d20` - Roll a d20\n• `2d6+3` - Roll 2d6 and add 3\n• `4d6kh3` - Roll 4d6, keep highest 3",
                color=0xff0000
            )
            await interaction.response.send_message(embed=error_embed)

    @bot.tree.command(name='initiative', description='Add character to initiative tracker')
    @app_commands.describe(
        name='Character name',
        roll='Initiative roll value'
    )
    async def add_initiative(interaction: discord.Interaction, name: str, roll: int):
        """Add to initiative tracker"""
        guild_id = interaction.guild.id
        bot.data_manager.add_initiative(guild_id, name, roll)
        
        # Get sorted initiative list
        initiatives = bot.data_manager.get_initiative_order(guild_id)
        
        embed = discord.Embed(
            title="⚔️ Initiative Tracker",
            color=0xffd93d
        )
        
        if initiatives:
            init_list = []
            for i, (char_name, init_roll) in enumerate(initiatives, 1):
                init_list.append(f"{i}. **{char_name}** - {init_roll}")
            
            embed.description = "\n".join(init_list)
        else:
            embed.description = "No characters in initiative"
            
        embed.set_footer(text=f"Added {name} with initiative {roll}")
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name='clearinitiative', description='Clear the initiative tracker')
    async def clear_initiative(interaction: discord.Interaction):
        """Clear initiative tracker"""
        guild_id = interaction.guild.id
        bot.data_manager.clear_initiative(guild_id)
        
        embed = discord.Embed(
            title="⚔️ Initiative Cleared",
            description="Initiative tracker has been reset",
            color=0x95a5a6
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name='addchar', description='Add a character to the database')
    @app_commands.describe(
        name='Character name',
        hp='Character HP'
    )
    async def add_character(interaction: discord.Interaction, name: str, hp: int):
        """Add character to database"""
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        bot.data_manager.add_character(guild_id, user_id, name, hp)
        
        embed = discord.Embed(
            title="📝 Character Added",
            color=0x2ecc71
        )
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="HP", value=str(hp), inline=True)
        embed.add_field(name="Owner", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name='checkchar', description='Check character details')
    @app_commands.describe(name='Character name to check')
    async def check_character(interaction: discord.Interaction, name: str):
        """Check character details"""
        guild_id = interaction.guild.id
        character = bot.data_manager.get_character(guild_id, name)
        
        if character:
            embed = discord.Embed(
                title="📋 Character Details",
                color=0x3498db
            )
            embed.add_field(name="Name", value=character['name'], inline=True)
            embed.add_field(name="HP", value=str(character['hp']), inline=True)
            
            # Get owner mention
            owner = bot.get_user(character['owner_id'])
            if owner:
                embed.add_field(name="Owner", value=owner.mention, inline=True)
            
        else:
            embed = discord.Embed(
                title="❌ Character Not Found",
                description=f"No character named '{name}' found in this server",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed)
