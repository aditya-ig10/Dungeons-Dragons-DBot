# Overview

This is a Discord bot designed for Dungeons & Dragons gameplay and server moderation. The bot provides essential D&D features like dice rolling, initiative tracking, and character management, along with moderation tools and music playback capabilities. It's specifically designed to run 24/7 on Replit using a Flask web server to maintain uptime.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
The bot is built using the discord.py library with slash commands (app_commands) for modern Discord interaction patterns. The main bot class extends `commands.Bot` and uses Discord intents for message content, member events, and voice state tracking.

## Command Organization
Commands are organized into separate modules by functionality:
- **D&D Commands**: Dice rolling, initiative tracking, character management
- **Moderation Commands**: User banning, muting/unmuting with role-based permissions
- **Music Commands**: YouTube audio playback using youtube-dl and FFmpeg

## Data Storage
The bot uses an in-memory data management system with thread-safe operations. Data is organized by Discord guild (server) and includes:
- Character information (name, HP)
- Initiative tracking (combat order)
- Temporary storage for bot session data

## Dice System
A sophisticated dice parser supports D&D notation including:
- Basic rolls (1d20, 2d6+3)
- Keep highest/lowest mechanics (4d6kh3)
- Mathematical operations (+, -, *, /)
- Static values and modifiers

## Permission System
Moderation commands implement proper Discord permission checking:
- User permission validation
- Bot permission verification
- Role hierarchy enforcement
- Error handling for permission failures

## Hosting Architecture
The bot uses a dual-server approach for Replit hosting:
- Flask web server on port 8000 for health checks and uptime monitoring
- Discord bot running in the main thread
- Threading to run both services simultaneously

## Audio Processing
Music functionality uses:
- youtube-dl for YouTube audio extraction
- discord.py's PCMVolumeTransformer for audio streaming
- FFmpeg for audio processing and playback
- Voice channel management with proper connection handling

# External Dependencies

## Discord Integration
- **discord.py**: Primary Discord API library for bot functionality
- **Discord Developer Portal**: Bot token and application management

## Audio Processing
- **youtube-dl**: YouTube audio extraction and metadata retrieval
- **FFmpeg**: Audio processing and streaming (system dependency)
- **pytube**: Alternative YouTube library (referenced in requirements)

## Web Framework
- **Flask**: Web server for Replit hosting and health endpoints
- **Replit Platform**: 24/7 hosting environment with port 8000 exposure

## Development Tools
- **python-dotenv**: Environment variable management for secure token storage
- **threading**: Concurrent execution of Flask and Discord bot

## External Services
- **YouTube**: Audio content source for music playback
- **UptimeRobot**: External monitoring service to prevent Replit hibernation
- **Discord Voice Channels**: Real-time audio streaming infrastructure

## Environment Configuration
- **Environment Variables**: Discord bot token stored in .env file
- **Replit Secrets**: Secure token storage in production environment
- **Port Configuration**: Dynamic port assignment for Replit hosting