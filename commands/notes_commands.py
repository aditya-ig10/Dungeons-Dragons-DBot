"""
Note-taking and campaign management commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

async def setup_notes_commands(bot):
    """Setup note-taking commands"""
    
    @bot.tree.command(name='note', description='Add a campaign note')
    @app_commands.describe(
        title='Note title',
        content='Note content'
    )
    async def add_note(interaction: discord.Interaction, title: str, content: str):
        """Add campaign note"""
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        # Add note to data manager
        bot.data_manager.add_note(guild_id, user_id, title, content)
        
        embed = discord.Embed(
            title="📝 Note Added",
            color=0x3498db
        )
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Content", value=content[:500] + "..." if len(content) > 500 else content, inline=False)
        embed.add_field(name="Author", value=interaction.user.mention, inline=True)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='notes', description='View all campaign notes')
    async def view_notes(interaction: discord.Interaction):
        """View all notes"""
        guild_id = interaction.guild.id
        notes = bot.data_manager.get_all_notes(guild_id)
        
        if not notes:
            embed = discord.Embed(
                title="📝 Campaign Notes",
                description="No notes found. Use `/note` to add one!",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Create paginated embeds if too many notes
        embed = discord.Embed(
            title="📝 Campaign Notes",
            color=0x3498db
        )
        
        for i, note in enumerate(notes[-10:], 1):  # Show last 10 notes
            author = bot.get_user(note['author_id'])
            author_name = author.display_name if author else "Unknown"
            
            embed.add_field(
                name=f"{i}. {note['title']}",
                value=f"{note['content'][:100]}{'...' if len(note['content']) > 100 else ''}\n*by {author_name}*",
                inline=False
            )
        
        if len(notes) > 10:
            embed.set_footer(text=f"Showing last 10 of {len(notes)} notes")
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='location', description='Set current party location')
    @app_commands.describe(location='Current location description')
    async def set_location(interaction: discord.Interaction, location: str):
        """Set party location"""
        guild_id = interaction.guild.id
        bot.data_manager.set_location(guild_id, location, interaction.user.id)
        
        embed = discord.Embed(
            title="🗺️ Location Updated",
            description=f"Party is now at: **{location}**",
            color=0xe67e22
        )
        embed.set_footer(text=f"Updated by {interaction.user.display_name}")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='quest', description='Add or update a quest')
    @app_commands.describe(
        title='Quest title',
        description='Quest description',
        status='Quest status (active, completed, failed)'
    )
    async def add_quest(interaction: discord.Interaction, title: str, description: str, status: str = "active"):
        """Add or update quest"""
        valid_statuses = ["active", "completed", "failed", "on_hold"]
        if status.lower() not in valid_statuses:
            embed = discord.Embed(
                title="❌ Invalid Status",
                description=f"Status must be one of: {', '.join(valid_statuses)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        bot.data_manager.add_quest(guild_id, user_id, title, description, status.lower())
        
        # Status colors
        status_colors = {
            "active": 0x3498db,
            "completed": 0x2ecc71,
            "failed": 0xe74c3c,
            "on_hold": 0xf39c12
        }
        
        # Status emojis
        status_emojis = {
            "active": "🎯",
            "completed": "✅",
            "failed": "❌",
            "on_hold": "⏸️"
        }
        
        embed = discord.Embed(
            title=f"{status_emojis[status.lower()]} Quest {status.title()}",
            color=status_colors[status.lower()]
        )
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Status", value=status.title(), inline=True)
        embed.add_field(name="Added by", value=interaction.user.mention, inline=True)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='quests', description='View all active quests')
    async def view_quests(interaction: discord.Interaction):
        """View all quests"""
        guild_id = interaction.guild.id
        quests = bot.data_manager.get_all_quests(guild_id)
        
        if not quests:
            embed = discord.Embed(
                title="🎯 Campaign Quests",
                description="No quests found. Use `/quest` to add one!",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Group by status
        status_emojis = {
            "active": "🎯",
            "completed": "✅",
            "failed": "❌",
            "on_hold": "⏸️"
        }
        
        embed = discord.Embed(
            title="🎯 Campaign Quests",
            color=0x3498db
        )
        
        # Group quests by status
        grouped_quests = {}
        for quest in quests:
            status = quest['status']
            if status not in grouped_quests:
                grouped_quests[status] = []
            grouped_quests[status].append(quest)
        
        # Add fields for each status
        for status in ["active", "on_hold", "completed", "failed"]:
            if status in grouped_quests:
                quest_list = []
                for quest in grouped_quests[status][-5:]:  # Last 5 per status
                    author = bot.get_user(quest['author_id'])
                    author_name = author.display_name if author else "Unknown"
                    quest_list.append(f"**{quest['title']}**\n{quest['description'][:80]}{'...' if len(quest['description']) > 80 else ''}")
                
                if quest_list:
                    embed.add_field(
                        name=f"{status_emojis[status]} {status.replace('_', ' ').title()} ({len(grouped_quests[status])})",
                        value="\n\n".join(quest_list),
                        inline=False
                    )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='session', description='Start a new session log')
    @app_commands.describe(session_name='Session name or number')
    async def start_session(interaction: discord.Interaction, session_name: str):
        """Start new session"""
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        bot.data_manager.start_session(guild_id, user_id, session_name)
        
        embed = discord.Embed(
            title="🎭 New Session Started",
            description=f"**{session_name}**",
            color=0x9b59b6
        )
        embed.add_field(name="Started by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Started at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
        
        # Try to join voice channel if user is in one
        voice_status = "Session started!"
        if interaction.user.voice:
            try:
                channel = interaction.user.voice.channel
                
                # Check permissions
                if channel.permissions_for(interaction.guild.me).connect:
                    # Connect to voice channel
                    voice_client = interaction.guild.voice_client
                    if voice_client is None:
                        await channel.connect()
                        voice_status = f"Joined {channel.mention} for the session!"
                    elif voice_client.channel != channel:
                        await voice_client.move_to(channel)
                        voice_status = f"Moved to {channel.mention} for the session!"
                    else:
                        voice_status = f"Already connected to {channel.mention}"
                else:
                    voice_status = "Session started! (No permission to join voice channel)"
            except Exception as e:
                voice_status = "Session started! (Couldn't join voice channel)"
        
        embed.add_field(name="Voice", value=voice_status, inline=False)
        embed.set_footer(text="Use /note to add session notes!")
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='leave', description='End session and leave voice channel')
    async def end_session(interaction: discord.Interaction):
        """End session and leave voice channel"""
        voice_client = interaction.guild.voice_client
        
        if voice_client is None:
            embed = discord.Embed(
                title="🎭 Session Status",
                description="Not currently connected to a voice channel",
                color=0x95a5a6
            )
        else:
            try:
                await voice_client.disconnect()
                embed = discord.Embed(
                    title="🎭 Session Ended",
                    description="Left the voice channel. Session concluded!",
                    color=0x9b59b6
                )
                embed.add_field(name="Ended by", value=interaction.user.mention, inline=True)
                embed.add_field(name="Ended at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Couldn't leave the voice channel",
                    color=0xff0000
                )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='inventory', description='Add item to party inventory')
    @app_commands.describe(
        item_name='Item name',
        quantity='Quantity (default: 1)',
        description='Item description (optional)'
    )
    async def add_inventory(interaction: discord.Interaction, item_name: str, quantity: int = 1, description: str = None):
        """Add item to inventory"""
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        bot.data_manager.add_inventory_item(guild_id, user_id, item_name, quantity, description)
        
        embed = discord.Embed(
            title="🎒 Item Added to Inventory",
            color=0x8e44ad
        )
        embed.add_field(name="Item", value=item_name, inline=True)
        embed.add_field(name="Quantity", value=str(quantity), inline=True)
        embed.add_field(name="Added by", value=interaction.user.mention, inline=True)
        
        if description:
            embed.add_field(name="Description", value=description, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='bag', description='View party inventory')
    async def view_inventory(interaction: discord.Interaction):
        """View party inventory"""
        guild_id = interaction.guild.id
        items = bot.data_manager.get_inventory(guild_id)
        
        if not items:
            embed = discord.Embed(
                title="🎒 Party Inventory",
                description="Inventory is empty. Use `/inventory` to add items!",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="🎒 Party Inventory",
            color=0x8e44ad
        )
        
        for item in items:
            author = bot.get_user(item['added_by'])
            author_name = author.display_name if author else "Unknown"
            
            value = f"Quantity: {item['quantity']}\nAdded by: {author_name}"
            if item['description']:
                value += f"\n*{item['description']}*"
            
            embed.add_field(
                name=item['name'],
                value=value,
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)