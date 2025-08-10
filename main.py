# main.py (for Background Worker)
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import sys
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found")
    raise ValueError("DISCORD_TOKEN is required")

_bot_instance = None
_bot_lock = threading.Lock()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        super().__init__(command_prefix='!', intents=intents)
        logger.info(f"Initializing MyBot instance {id(self)}")
        if not hasattr(self, 'tree'):
            self.tree = app_commands.CommandTree(self)
            logger.info("CommandTree initialized")
        else:
            logger.warning("CommandTree already exists, skipping initialization")

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
                logger.info(f"Returning existing MyBot instance {id(_bot_instance)}")
            return _bot_instance

    async def start_with_retry(self, token, max_attempts=10, initial_delay=60, backoff_factor=2):
        attempt = 1
        delay = initial_delay
        while attempt <= max_attempts:
            try:
                logger.info(f"Login attempt {attempt}/{max_attempts}")
                await self.start(token)
                return
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    logger.warning(f"Rate limited, retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay *= backoff_factor
                else:
                    logger.error(f"Login failed: {e}", exc_info=True)
                    raise
            except Exception as e:
                logger.error(f"Login failed: {e}", exc_info=True)
                raise
        logger.error("Max login attempts reached, exiting")
        raise Exception("Failed to login after max attempts")

    async def close(self):
        logger.info("Closing bot and cleaning up sessions")
        await super().close()
        if self.http.connector is not None:
            logger.info(f"Closing connector: {self.http.connector}")
            await self.http.connector.close()
            logger.info("HTTP connector closed")
        else:
            logger.warning("No HTTP connector to close")

if __name__ == '__main__':
    logger.info("Starting application")
    try:
        bot = MyBot.get_instance()
        logger.info(f"Running bot instance {id(bot)}")
        asyncio.run(bot.start_with_retry(TOKEN))
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down")
        asyncio.run(bot.close())
    except Exception as e:
        logger.error(f"Failed to run bot: {e}", exc_info=True)
        asyncio.run(bot.close())
        raise