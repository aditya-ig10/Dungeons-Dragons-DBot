"""
Dungeon Master commands: HP management, damage, healing, combat tracking
"""
import discord
from discord import app_commands
from discord.ext import commands
from utils.dice_parser import DiceParser

async def setup_dm_commands(bot):
    """Setup DM-only commands"""
    
    def is_dm():
        """Check if user has DM permissions (Manage Server or Admin)"""
        async def predicate(interaction: discord.Interaction) -> bool:
            return (interaction.user.guild_permissions.manage_guild or 
                   interaction.user.guild_permissions.administrator)
        return app_commands.check(predicate)
    
    @bot.tree.command(name='dmhp', description='[DM Only] Set character HP')
    @app_commands.describe(
        character='Character name',
        new_hp='New HP value'
    )
    @is_dm()
    async def dm_set_hp(interaction: discord.Interaction, character: str, new_hp: int):
        """DM set character HP"""
        guild_id = interaction.guild.id
        char_data = bot.data_manager.get_character(guild_id, character)
        
        if not char_data:
            embed = discord.Embed(
                title="❌ Character Not Found",
                description=f"No character named '{character}' found",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Update HP
        bot.data_manager.update_character_hp(guild_id, character, new_hp)
        
        embed = discord.Embed(
            title="⚔️ DM Updated HP",
            color=0xe74c3c
        )
        embed.add_field(name="Character", value=character, inline=True)
        embed.add_field(name="New HP", value=str(new_hp), inline=True)
        embed.add_field(name="DM", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='damage', description='[DM Only] Deal damage to character')
    @app_commands.describe(
        character='Character name',
        damage='Damage amount or dice (e.g., 8 or 2d6+3)',
        damage_type='Type of damage (optional)'
    )
    @is_dm()
    async def deal_damage(interaction: discord.Interaction, character: str, damage: str, damage_type: str = None):
        """DM deal damage to character"""
        guild_id = interaction.guild.id
        char_data = bot.data_manager.get_character(guild_id, character)
        
        if not char_data:
            embed = discord.Embed(
                title="❌ Character Not Found",
                description=f"No character named '{character}' found",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        try:
            # Parse damage (could be dice or number)
            if damage.isdigit():
                damage_amount = int(damage)
                damage_details = f"Static damage: {damage_amount}"
            else:
                parser = DiceParser()
                result = parser.parse_and_roll(damage)
                damage_amount = result['total']
                damage_details = result['details']
            
            # Calculate new HP
            current_hp = char_data['hp']
            new_hp = max(0, current_hp - damage_amount)
            
            # Update HP
            bot.data_manager.update_character_hp(guild_id, character, new_hp)
            
            # Create embed
            embed = discord.Embed(
                title="💥 Damage Dealt",
                color=0xe74c3c
            )
            embed.add_field(name="Character", value=character, inline=True)
            embed.add_field(name="Damage", value=f"{damage_amount}", inline=True)
            embed.add_field(name="HP", value=f"{current_hp} → {new_hp}", inline=True)
            
            if damage_type:
                embed.add_field(name="Damage Type", value=damage_type, inline=True)
            
            embed.add_field(name="Roll Details", value=damage_details, inline=False)
            embed.set_footer(text=f"DM: {interaction.user.display_name}")
            
            # Add status indicator
            if new_hp == 0:
                embed.add_field(name="⚠️ Status", value="**UNCONSCIOUS**", inline=True)
            elif new_hp < char_data['max_hp'] * 0.25:
                embed.add_field(name="⚠️ Status", value="Critically wounded", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Invalid Damage",
                description=f"Error: {str(e)}\n\nExamples:\n• `8` - Deal 8 damage\n• `2d6+3` - Roll damage dice",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='heal', description='[DM Only] Heal character')
    @app_commands.describe(
        character='Character name',
        healing='Healing amount or dice (e.g., 8 or 2d4+2)',
        heal_type='Type of healing (optional)'
    )
    @is_dm()
    async def heal_character(interaction: discord.Interaction, character: str, healing: str, heal_type: str = None):
        """DM heal character"""
        guild_id = interaction.guild.id
        char_data = bot.data_manager.get_character(guild_id, character)
        
        if not char_data:
            embed = discord.Embed(
                title="❌ Character Not Found",
                description=f"No character named '{character}' found",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        try:
            # Parse healing (could be dice or number)
            if healing.isdigit():
                heal_amount = int(healing)
                heal_details = f"Static healing: {heal_amount}"
            else:
                parser = DiceParser()
                result = parser.parse_and_roll(healing)
                heal_amount = result['total']
                heal_details = result['details']
            
            # Calculate new HP (don't exceed max HP)
            current_hp = char_data['hp']
            max_hp = char_data['max_hp']
            new_hp = min(max_hp, current_hp + heal_amount)
            actual_healing = new_hp - current_hp
            
            # Update HP
            bot.data_manager.update_character_hp(guild_id, character, new_hp)
            
            # Create embed
            embed = discord.Embed(
                title="💚 Healing Applied",
                color=0x2ecc71
            )
            embed.add_field(name="Character", value=character, inline=True)
            embed.add_field(name="Healing", value=f"{actual_healing}", inline=True)
            embed.add_field(name="HP", value=f"{current_hp} → {new_hp}", inline=True)
            
            if heal_type:
                embed.add_field(name="Heal Type", value=heal_type, inline=True)
            
            embed.add_field(name="Roll Details", value=heal_details, inline=False)
            
            if actual_healing < heal_amount:
                embed.add_field(name="Note", value=f"Healed {actual_healing} (limited by max HP)", inline=False)
            
            embed.set_footer(text=f"DM: {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Invalid Healing",
                description=f"Error: {str(e)}\n\nExamples:\n• `8` - Heal 8 HP\n• `2d4+2` - Roll healing dice",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='attack', description='[DM Only] Make attack roll for NPC/Monster')
    @app_commands.describe(
        attacker='Attacker name',
        target='Target character (optional)',
        attack_bonus='Attack bonus (optional)',
        damage_dice='Damage dice (e.g., 1d8+3)'
    )
    @is_dm()
    async def npc_attack(interaction: discord.Interaction, attacker: str, target: str = None, attack_bonus: int = 0, damage_dice: str = None):
        """DM make attack roll for NPC"""
        try:
            parser = DiceParser()
            
            # Roll attack (1d20 + bonus)
            attack_result = parser.parse_and_roll(f"1d20+{attack_bonus}")
            attack_total = attack_result['total']
            
            embed = discord.Embed(
                title="⚔️ Attack Roll",
                color=0xf39c12
            )
            embed.add_field(name="Attacker", value=attacker, inline=True)
            embed.add_field(name="Attack Roll", value=f"**{attack_total}**", inline=True)
            embed.add_field(name="Details", value=attack_result['details'], inline=True)
            
            if target:
                embed.add_field(name="Target", value=target, inline=True)
            
            # Roll damage if provided
            if damage_dice:
                damage_result = parser.parse_and_roll(damage_dice)
                embed.add_field(name="Damage Roll", value=f"**{damage_result['total']}**", inline=True)
                embed.add_field(name="Damage Details", value=damage_result['details'], inline=True)
            
            embed.set_footer(text=f"DM: {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Invalid Attack",
                description=f"Error: {str(e)}\n\nExample: `/attack Goblin Aragorn 5 1d6+2`",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name='status', description='[DM Only] View all character status')
    @is_dm()
    async def party_status(interaction: discord.Interaction):
        """DM view all character status"""
        guild_id = interaction.guild.id
        characters = bot.data_manager.get_all_characters(guild_id)
        
        if not characters:
            embed = discord.Embed(
                title="📋 Party Status",
                description="No characters found in this server",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Party Status",
            description="Current HP status of all characters",
            color=0x3498db
        )
        
        for char in characters:
            hp_percent = (char['hp'] / char['max_hp']) * 100
            
            # Status indicator
            if char['hp'] == 0:
                status = "💀 Unconscious"
            elif hp_percent < 25:
                status = "🔴 Critical"
            elif hp_percent < 50:
                status = "🟡 Wounded"
            else:
                status = "🟢 Healthy"
            
            # Get owner
            owner = bot.get_user(char['owner_id'])
            owner_name = owner.display_name if owner else "Unknown"
            
            embed.add_field(
                name=f"{char['name']} ({owner_name})",
                value=f"{char['hp']}/{char['max_hp']} HP\n{status}",
                inline=True
            )
        
        embed.set_footer(text=f"DM: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)