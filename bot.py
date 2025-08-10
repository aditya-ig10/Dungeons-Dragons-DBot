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
        
        # Add help command
        @self.tree.command(name='help', description='Show all available commands')
        async def help_command(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🎲 D&D Bot Commands",
                description="Here are all available commands:",
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
            
            embed.set_footer(text="Bot created for D&D gameplay and server management")
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
