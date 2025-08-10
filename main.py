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

bot = MyBot()

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Dungeons & Dragons"))

@bot.event
async def on_member_join(member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(f"Welcome to the server, {member.mention}! Ready for some D&D?")

@bot.tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
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

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

bot.run(TOKEN)