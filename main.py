# main.py
import discord
from discord import app_commands
from discord.ext import commands
import threading
from flask import Flask
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    raise ValueError("DISCORD_TOKEN is required")

# Singleton pattern for bot instance
_bot_instance = None
_bot_lock = threading.Lock()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        super().__init__(command_prefix='!', intents=intents)
        logger.info("Initializing MyBot")
        # Only create CommandTree if not already set
        if not hasattr(self, 'tree'):
            self.tree = app_commands.CommandTree(self)
            logger.info("CommandTree initialized")

    async def setup_hook(self):
        logger.info("Loading extensions")
        try:
            await self.load_extension('commands.dnd_commands')
            await self.load_extension('commands.dm_commands')
            await self.load_extension('commands.notes_commands')
            await self.load_extension('commands.music_commands')
            await self.load_extension('commands.moderation_commands')
            logger.info("Extensions loaded successfully")
            await self.tree.sync()
            logger.info("Command tree synced")
        except Exception as e:
            logger.error(f"Failed to load extensions or sync tree: {e}", exc_info=True)
            raise

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.change_presence(activity=discord.Game(name="Dungeons & Dragons"))

    async def on_member_join(self, member):
        if member.guild.system_channel:
            await member.guild.system_channel.send(f"Welcome to the server, {member.mention}! Ready for some D&D?")

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        else:
            logger.error(f"Command tree error: {error}", exc_info=True)
            await interaction.response.send_message("An error occurred.", ephemeral=True)

    @classmethod
    def get_instance(cls):
        global _bot_instance
        with _bot_lock:
            if _bot_instance is None:
                logger.info("Creating new MyBot instance")
                _bot_instance = cls()
            else:
                logger.info("Returning existing MyBot instance")
            return _bot_instance

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    logger.info("Starting Flask server")
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    logger.info("Starting application")
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Ensure Flask thread exits when main thread does
    flask_thread.start()

    # Run the bot
    try:
        bot = MyBot.get_instance()
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to run bot: {e}", exc_info=True)
        raise