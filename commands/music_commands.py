# commands/music_commands.py
import logging
from discord.ext import commands
import discord
from discord import app_commands
import youtube_dl

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play audio from YouTube in voice channel")
    @app_commands.describe(url="YouTube URL or search term")
    async def play(self, interaction: discord.Interaction, url: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message("You must be in a voice channel.", ephemeral=True)
            return
        channel = user.voice.channel
        voice_client = interaction.guild.voice_client
        if not voice_client:
            voice_client = await channel.connect()
        await interaction.response.defer()
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info.get('url', info['entries'][0]['url'] if 'entries' in info else None)
            voice_client.play(discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
            await interaction.followup.send(f"Playing: {info['title']}")
        except Exception as e:
            logging.error(e)
            await interaction.followup.send("Failed to play audio.", ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and disconnect from voice")
    async def stop(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        voice_client = interaction.guild.voice_client
        if voice_client:
            voice_client.stop()
            await voice_client.disconnect()
            await interaction.response.send_message("Stopped music and disconnected.")
        else:
            await interaction.response.send_message("Not connected to voice.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))