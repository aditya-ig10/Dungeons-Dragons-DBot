import discord
from discord import app_commands

class HelpCommands(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="help", description="Display bot commands and information")
        self.bot = bot

    @app_commands.command(name="commands", description="Show all available commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 D&D Bot Commands",
            description="Your complete D&D companion bot!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else "")
        embed.set_footer(text="DnD.io Bot | Created by Aditya")

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
                "`/session <name>` - Start new session"
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

        embed.add_field(
            name="✨ Enhanced Features",
            value="Enhanced D&D bot with campaign management, combat, and notes!",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

def setup(bot):
    bot.tree.add_command(HelpCommands(bot))