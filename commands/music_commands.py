"""
Music commands: play, stop (YouTube support)
"""
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import youtube_dl
import os

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def setup_music_commands(bot):
    """Setup music commands"""
    
    @bot.tree.command(name='play', description='Play audio from YouTube URL')
    @app_commands.describe(url='YouTube URL to play')
    async def play_music(interaction: discord.Interaction, url: str):
        """Play music command"""
        # Check if user is in a voice channel
        if not interaction.user.voice:
            embed = discord.Embed(
                title="❌ Not in Voice Channel",
                description="You need to be in a voice channel to use this command",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        # Check bot permissions
        if not channel.permissions_for(interaction.guild.me).connect:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to join this voice channel",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not channel.permissions_for(interaction.guild.me).speak:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to speak in this voice channel",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Defer the response as YouTube processing might take time
        await interaction.response.defer()
        
        try:
            # Connect to voice channel
            voice_client = interaction.guild.voice_client
            if voice_client is None:
                voice_client = await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
            
            # Stop current audio if playing
            if voice_client.is_playing():
                voice_client.stop()
            
            # Get audio source
            try:
                player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ YouTube Error",
                    description=f"Could not process YouTube URL: {str(e)[:100]}...",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Play audio
            voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            
            # Success embed
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{player.title}**",
                color=0x00ff00
            )
            embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except discord.ClientException as e:
            embed = discord.Embed(
                title="❌ Connection Error",
                description="Could not connect to voice channel or audio is already playing",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {str(e)[:100]}...",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)

    @bot.tree.command(name='stop', description='Stop music playback and disconnect')
    async def stop_music(interaction: discord.Interaction):
        """Stop music command"""
        voice_client = interaction.guild.voice_client
        
        if voice_client is None:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user is in the same voice channel
        if interaction.user.voice is None or interaction.user.voice.channel != voice_client.channel:
            embed = discord.Embed(
                title="❌ Different Channel",
                description="You need to be in the same voice channel as the bot",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Stop playing and disconnect
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            
            embed = discord.Embed(
                title="⏹️ Music Stopped",
                description="Disconnected from voice channel",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
