# main.py
import discord
from discord import app_commands
from discord.ext import commands
import threading
from flask import Flask
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Singleton pattern to ensure only one bot instance
_bot_instance = None

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        super().__init__(command_prefix='!', intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.load_extension('commands.dnd_commands')
        await self.load_extension('commands.dm_commands')
        await self.load_extension('commands.notes_commands')
        await self.load_extension('commands.music_commands')
        await self.load_extension('commands.moderation_commands')
        await self.tree.sync()

    @classmethod
    def get_instance(cls):
        global _bot_instance
        if _bot_instance is None:
            _bot_instance = cls()
        return _bot_instance

@commands.Bot.event
async def on_ready(self):
    logging.info(f'Logged in as {self.user}')
    await self.change_presence(activity=discord.Game(name="Dungeons & Dragons"))

@commands.Bot.event
async def on_member_join(self, member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(f"Welcome to the server, {member.mention}! Ready for some D&D?")

@commands.Bot.tree.error
async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        logging.error(error)
        await interaction.response.send_message("An error occurred.", ephemeral=True)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Ensure Flask thread exits when main thread does
    flask_thread.start()

    # Run the bot
    bot = MyBot.get_instance()
    bot.run(TOKEN)