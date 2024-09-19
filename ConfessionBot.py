import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Set up bot and intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!RemIsGay", intents=intents)  # It's required lmao might as well make it funny, it doesn't do anything tho

# Define paths and default settings
CONFIG_DIR = "server_configs"  # Directory for server configuration files
DEFAULT_CONFIG = {
    "admin_roles": [],
    "confession_channel_ids": [],
    "banned_users": [],
    "confessions": []
}

def get_config(server_id):
    """
    Load the configuration for the given server.
    """
    config_path = os.path.join(CONFIG_DIR, f"{server_id}.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    return DEFAULT_CONFIG

def save_config(server_id, config):
    """
    Save the configuration for the given server.
    """
    config_path = os.path.join(CONFIG_DIR, f"{server_id}.json")
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

@bot.tree.command(name="confess", description="Submit an anonymous confession")
async def confess(interaction: discord.Interaction, message: str):
    """
    Handle the submission of an anonymous confession.
    """
    server_id = str(interaction.guild.id)
    config = get_config(server_id)
    
    # Check if the command is used in an allowed channel
    if interaction.channel.id not in config["confession_channel_ids"]:
        await interaction.response.send_message("You cannot use this command in this channel.", ephemeral=True)
        return

    # Check if the user is banned
    if interaction.user.id in config["banned_users"]:
        await interaction.response.send_message("You are banned from using this confession bot.", ephemeral=True)
        return

    # Add confession to the list and keep only the latest 5
    confession_id = len(config["confessions"]) + 1
    config["confessions"].append({"id": confession_id, "message": message, "user_id": interaction.user.id})
    if len(config["confessions"]) > 5:
        config["confessions"].pop(0)

    save_config(server_id, config)
    # Send the confession to all configured confession channels
    for channel_id in config["confession_channel_ids"]:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Confession #{confession_id}: {message}")

    await interaction.response.send_message("Your confession has been submitted.", ephemeral=True)

@bot.tree.command(name="configure", description="Configure server settings for the confession bot")
@commands.has_permissions(administrator=True)
async def configure(interaction: discord.Interaction, admin_role_ids: str, confession_channel_ids: str):
    """
    Configure server settings for the confession bot.
    """
    server_id = str(interaction.guild.id)
    config = get_config(server_id)
    
    # Parse role and channel IDs from the input
    admin_role_ids = [int(role_id.strip('<@&>')) for role_id in admin_role_ids.split(',')]
    confession_channel_ids = [int(channel_id.strip('<#>')) for channel_id in confession_channel_ids.split(',')]
    
    config["admin_roles"] = admin_role_ids
    config["confession_channel_ids"] = confession_channel_ids
    save_config(server_id, config)
    
    await interaction.response.send_message("Server configuration updated.", ephemeral=True)

def has_required_role(interaction: discord.Interaction, config):
    """
    Check if the user has the required role or administrator permissions.
    """
    user_roles = [role.id for role in interaction.user.roles]
    has_role = any(role_id in user_roles for role_id in config["admin_roles"])
    has_admin_perm = interaction.user.guild_permissions.administrator
    return has_role or has_admin_perm

@bot.tree.command(name="confession_ban", description="Ban a user from using the confession bot")
async def confession_ban(interaction: discord.Interaction, confession_number: int):
    """
    Ban a user from using the confession bot based on the confession number.
    """
    server_id = str(interaction.guild.id)
    config = get_config(server_id)

    if not has_required_role(interaction, config):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    confession = next((conf for conf in config["confessions"] if conf["id"] == confession_number), None)
    if confession:
        user_id = confession["user_id"]
        if user_id not in config["banned_users"]:
            config["banned_users"].append(user_id)
            save_config(server_id, config)
            await interaction.response.send_message("User Banned", ephemeral=True)
        else:
            await interaction.response.send_message("User is already banned.", ephemeral=True)
    else:
        await interaction.response.send_message("Confession not found.", ephemeral=True)

@bot.tree.command(name="confession_unban", description="Unban a user from using the confession bot")
async def confession_unban(interaction: discord.Interaction, user_mention: str):
    """
    Unban a user from using the confession bot.
    """
    server_id = str(interaction.guild.id)
    config = get_config(server_id)

    if not has_required_role(interaction, config):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    user_id = int(user_mention.strip('<@!>'))
    if user_id in config["banned_users"]:
        config["banned_users"].remove(user_id)
        save_config(server_id, config)
        await interaction.response.send_message("User unbanned successfully.", ephemeral=True)
    else:
        await interaction.response.send_message("User is not banned.", ephemeral=True)

@bot.tree.command(name="expose", description="Expose a confession and notify involved users")
async def expose(interaction: discord.Interaction, confession_number: int):
    """
    Expose a confession and notify the involved users.
    """
    server_id = str(interaction.guild.id)
    config = get_config(server_id)

    if not has_required_role(interaction, config):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    confession = next((conf for conf in config["confessions"] if conf["id"] == confession_number), None)
    if confession:
        user_id = confession["user_id"]
        guild = bot.get_guild(interaction.guild.id)
        admin_user_id = interaction.user.id

        try:
            user = guild.get_member(user_id)
            if user is None:
                user = await guild.fetch_member(user_id)
            if user is None:
                raise discord.NotFound("User not found in the server")
        except discord.NotFound:
            user = None

        if user:
            try:
                await user.send(f"You have been exposed! Confession #{confession_number}: {confession['message']}.\nExposed by: {interaction.user.name}")
                exposed_username = user.name
            except discord.Forbidden:
                exposed_username = "Unknown User (DMs disabled)"
        else:
            exposed_username = "Unknown User (Not in the server)"

        try:
            await interaction.user.send(f"You exposed confession #{confession_number}. User {exposed_username}")
        except discord.Forbidden:
            await interaction.response.send_message("Unable to send a DM to the admin.", ephemeral=True)

        await interaction.response.send_message(f"Exposure notifications sent. User {exposed_username}.", ephemeral=True)
    else:
        await interaction.response.send_message("Confession not found.", ephemeral=True)

@bot.eventMTI4NjQwMzYwNzQ2NTQzMTA0MA.GmVPh-.jdx-ef69xJpINmVwWRTFeKvivTKKsLr29LPcqc
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync() 
    print("Slash commands synced.")

bot.run('YourBotTokenHere')