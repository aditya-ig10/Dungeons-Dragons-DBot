"""
Main Discord bot implementation with event handlers and command setup
"""
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from commands.dnd_commands import setup_dnd_commands
from commands.moderation_commands import setup_moderation_commands
from commands.music_commands import setup_music_commands
from commands.dm_commands import setup_dm_commands
from commands.notes_commands import setup_notes_commands
from utils.data_manager import DataManager

# Load environment variables
load_dotenv()

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.members = True         # Required for welcome messages and member info
intents.voice_states = True    # Required for music commands

class DnDBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        self.data_manager = DataManager()
    
    async def setup_hook(self):
        """Setup hook called when the bot is ready"""
        # Setup command groups
        await setup_dnd_commands(self)
        await setup_moderation_commands(self)
        await setup_music_commands(self)
        await setup_dm_commands(self)
        await setup_notes_commands(self)
        
        # Add help command
        @self.tree.command(name='help', description='Show all available commands')
        async def help_command(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🎲 D&D Bot Commands",
                description="Your complete D&D companion bot!",
                color=0x7289DA
            )
            
            # D&D Commands
            embed.add_field(
                name="🎲 D&D Commands",
                value=(
                    "`/roll <dice>` - Roll dice (e.g., 2d6+3)\n"
                    "`/initiative <name> <roll>` - Add to initiative tracker\n"
                    "`/clearinitiative` - Clear initiative tracker\n"
                    "`/addchar <name> <hp>` - Add character\n"
                    "`/checkchar <name>` - Check character details"
                ),
                inline=False
            )
            
            # DM Commands
            embed.add_field(
                name="⚔️ DM Commands (Manage Server permission required)",
                value=(
                    "`/dmhp <character> <hp>` - Set character HP\n"
                    "`/damage <character> <amount>` - Deal damage\n"
                    "`/heal <character> <amount>` - Heal character\n"
                    "`/attack <attacker> [target] [bonus] [damage]` - NPC attack\n"
                    "`/status` - View all character status"
                ),
                inline=False
            )
            
            # Campaign Management
            embed.add_field(
                name="📝 Campaign Management",
                value=(
                    "`/note <title> <content>` - Add campaign note\n"
                    "`/notes` - View all notes\n"
                    "`/quest <title> <description> [status]` - Add quest\n"
                    "`/quests` - View all quests\n"
                    "`/location <place>` - Set party location\n"
                    "`/session <name>` - Start new session & join voice\n"
                    "`/leave` - End session & leave voice channel"
                ),
                inline=False
            )
            
            # Inventory
            embed.add_field(
                name="🎒 Inventory",
                value=(
                    "`/inventory <item> [quantity] [description]` - Add item\n"
                    "`/bag` - View party inventory"
                ),
                inline=False
            )
            
            # Music Commands
            embed.add_field(
                name="🎵 Music Commands",
                value=(
                    "`/play <url>` - Play YouTube audio\n"
                    "`/stop` - Stop music and disconnect"
                ),
                inline=False
            )
            
            # Moderation Commands
            embed.add_field(
                name="🛡️ Moderation Commands",
                value=(
                    "`/ban <user> [reason]` - Ban a user\n"
                    "`/mute <user> <minutes> [reason]` - Mute a user\n"
                    "`/unmute <user>` - Unmute a user"
                ),
                inline=False
            )
            
            embed.set_footer(text="Enhanced D&D bot with campaign management, combat, and notes!")
            await interaction.response.send_message(embed=embed)
        
        # Sync commands
        await self.tree.sync()
        print(f"Synced commands for {self.user}")

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot activity
        activity = discord.Game(name="D&D | /help for commands")
        await self.change_presence(activity=activity)

    async def on_member_join(self, member):
        """Welcome new members"""
        if member.bot:
            return
            
        # Send welcome message to system channel
        if member.guild.system_channel:
            embed = discord.Embed(
                title="🎲 Welcome to the Server!",
                description=f"Welcome {member.mention}! Ready for some D&D adventures?",
                color=0x00ff00
            )
            embed.add_field(
                name="Getting Started",
                value=(
                    "Use `/help` to see all available commands!\n"
                    "Roll dice with `/roll 1d20`\n"
                    "Add your character with `/addchar`"
                ),
                inline=False
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text="Have fun and follow the server rules!")
            
            await member.guild.system_channel.send(embed=embed)

def run_bot():
    """Run the Discord bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
        return
    
    bot = DnDBot()
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token")
    except Exception as e:
        print(f"Error running bot: {e}")
