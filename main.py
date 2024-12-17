import nextcord
from nextcord.ext import commands, tasks
from nextcord import Intents, Embed, Interaction
import json
import random
import os
import re
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
import asyncio

config_path = os.path.join('util', 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

intents = Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

giveaways = {}
finished_giveaways = {}
special_role = config.get('special_role')

def has_permission(interaction: Interaction):
    return interaction.user.guild_permissions.administrator or any(role.name == special_role for role in interaction.user.roles)

def parse_duration(temps: str):
    try:
        days = hours = minutes = seconds = 0
        if 'd' in temps:
            days = int(re.search(r'(\d+)d', temps).group(1))
        if 'h' in temps:
            hours = int(re.search(r'(\d+)h', temps).group(1))
        if 'm' in temps:
            minutes = int(re.search(r'(\d+)m', temps).group(1))
        if 's' in temps:
            seconds = int(re.search(r'(\d+)s', temps).group(1))

        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    except Exception as e:
        print(f"Error when analysing duration : {e}")
        return None

def format_date_relative(date_debut: datetime, duration: timedelta):
    local_tz = get_localzone()
    date_fin = date_debut + duration
    date_fin_locale = date_fin.astimezone(local_tz)

    return date_fin_locale.strftime('%d/%m/%Y to %H:%M')

def giveaway_delay():
    config['giveaway_delay']
    

def format_duration(duration: timedelta):
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hours")
    if minutes > 0:
        parts.append(f"{minutes} minutes")
    if seconds > 0:
        parts.append(f"{seconds} seconds")

    return ", ".join(parts)

@bot.event
async def on_ready():
    print(f'The bot is ready. Connected as : {bot.user.name}')
    check_giveaways.start()

@bot.slash_command(name="giveaway", description="Start a giveaway")
async def tirage_au_sort(
    interaction: Interaction,
    temps: str = nextcord.SlashOption(description="Duration of giveaway (for example 1d2h3m4s)", required=True),
    prix: str = nextcord.SlashOption(description="Prizes for the giveaway (for example 1M VIP)", required=True),
    nombre_de_gagnants: int = nextcord.SlashOption(description="Numbers of winners", required=True),
    mention: str = nextcord.SlashOption(description="@everyone, @here or nothing", choices={"everyone": "everyone", "here": "here", "nothing": "nothing"}, required=True),
    description: str = nextcord.SlashOption(description="Description of the giveaway", required=False, default=""),
    conditions: str = nextcord.SlashOption(description="Conditions of participations", required=False, default="")
):
    if not has_permission(interaction):
        await interaction.response.send_message("You are not authorised to use this command.", ephemeral=True)
        return

    mention_text = ""
    if mention == "everyone":
        mention_text = "@everyone"
    elif mention == "here":
        mention_text = "@here"

    duration = parse_duration(temps)
    if not duration:
        await interaction.response.send_message("Invalid time format. Use a format such as 1d2h3m4s (days, hours, minutes, seconds).", ephemeral=True)
        return

    durée_en_secondes = duration.total_seconds()

    date_debut = datetime.now()
    date_fin_str = format_date_relative(date_debut, duration)

    embed = Embed(
        title="🎉 **GIVEAWAY** 🎉",
        description=f"Participate for Win ! **{prix}**!",
        color=0x000000,
        timestamp=interaction.created_at
    )
    embed.add_field(name="⏳ **Duration**", value=f"{format_duration(duration)}", inline=True)
    embed.add_field(name="🏆 **Numbers of winners**", value=f"{nombre_de_gagnants}", inline=True)
    if description:
        embed.add_field(name="📝 **Description**", value=description, inline=False)
    if conditions:
        embed.add_field(name="⚠️ **Conditions**", value=conditions, inline=False)
    embed.add_field(name="🗓️ **End Date**", value=f"```fix\n{date_fin_str}\n```", inline=False)
    embed.set_thumbnail(url="https://example.com/your-image.png")
    embed.set_image(url="https://cdn.leonardo.ai/users/8f3edea8-356a-4c94-affe-c3172c55172a/generations/838042a4-9ab9-4173-b17e-e44260b51ecc/Leonardo_Phoenix_A_vibrant_neonlit_image_featuring_the_bold_cu_1.jpg")
    embed.set_footer(text="Created by gxqk ✅", icon_url="https://i.ibb.co/thhnXgS/b38c0bbfc54a2ddff1769686652edf77.png")

    await interaction.response.send_message(content=mention_text, embed=embed)
    message = await interaction.original_message()
    await message.add_reaction("🎉")
    giveaways[message.id] = (interaction.channel.id, prix, nombre_de_gagnants, interaction.guild_id, durée_en_secondes)

    async def fin_giveaway(message_id):
        await bot.wait_until_ready()

        if message_id not in giveaways:
            print(f"The giveaway with the ID {message_id} don't appear in the database of giveaways.")
            return

        await asyncio.sleep(durée_en_secondes)

        channel_id, prix, nombre_de_gagnants, guild_id, _ = giveaways[message_id]
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        try:
            reaction = next(reaction for reaction in message.reactions if str(reaction.emoji) == "🎉")
            users = await reaction.users().flatten()
            users = [user for user in users if not user.bot]
        except nextcord.errors.NotFound:
            print(f"the message of giveaway with the ID {message_id} does not exist.")
            giveaways.pop(message_id)
            return

        if users:
            winners = random.sample(users, min(len(users), nombre_de_gagnants))
            winners_mentions = ", ".join(winner.mention for winner in winners)
            await channel.send(f"Congratulations {winners_mentions}, you have win the giveaway for **{prix}**!")
            embed_win = Embed(
                title="🎉 **YOU HAVE WIN** 🎉",
                description=f"You have won **{prix}** in the giveaway in the server {bot.get_guild(guild_id).name}!",
                color=0x000000
            )
            embed_win.set_image(url="https://t4.ftcdn.net/jpg/01/07/12/23/360_F_107122345_uXaVQsLkGDL4rP1hpLnqp9MbEYTIdunN.jpg")
            embed_win.set_footer(text="Created by gxqk ✅", icon_url="https://i.ibb.co/thhnXgS/b38c0bbfc54a2ddff1769686652edf77.png")
            for winner in winners:
                try:
                    await winner.send(embed=embed_win)
                except nextcord.Forbidden:
                    await channel.send(f"{winner.mention} have win but i cant send the message private.")
        else:
            await channel.send("There are no participants, the giveaway have finish without winner.")

        if message_id not in finished_giveaways:
            finished_giveaways[message_id] = True

    await fin_giveaway(message.id)

@bot.slash_command(name="reroll", description="Relaunch the prize draw to choose a new winner")
async def reroll(interaction: Interaction, message_id: str = nextcord.SlashOption(description="ID du message du tirage au sort", required=True)):
    if not has_permission(interaction):
        await interaction.response.send_message("You are not authorised to use this command.", ephemeral=True)
        return

    message_id_int = int(message_id)
    if message_id_int not in giveaways and message_id_int not in finished_giveaways:
        await interaction.response.send_message("The giveaway no longer exists or has already been completed.", ephemeral=True)
        return

    channel_id, prix, nombre_de_gagnants, guild_id, _ = giveaways.get(message_id_int) or finished_giveaways.get(message_id_int)
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id_int)
    
    try:
        reaction = next(reaction for reaction in message.reactions if str(reaction.emoji) == "🎉")
        users = await reaction.users().flatten()
        users = [user for user in users if not user.bot]
    except nextcord.errors.NotFound:
        await interaction.response.send_message("The giveaway no longer exists or has already been completed.", ephemeral=True)
        return

    if users:
        winners = random.sample(users, min(len(users), nombre_de_gagnants))
        winners_mentions = ", ".join(winner.mention for winner in winners)
        await channel.send(f"Congrulations {winners_mentions}, you have won the relaunch of the prize giveaway for **{prix}**!")
        embed_win = Embed(
            title="🎉 **YOU HAVE WIN** 🎉",
            description=f"You have won **{prix}** in the relaunch of the prize giveaway on the server {bot.get_guild(guild_id).name}!",
            color=0x000000
        )
        embed_win.set_footer(text="Created by gxqk ✅", icon_url="https://i.ibb.co/thhnXgS/b38c0bbfc54a2ddff1769686652edf77.png")
        for winner in winners:
            try:
                await winner.send(embed=embed_win)
            except nextcord.Forbidden:
                await channel.send(f"{winner.mention} won but I can't send a private message.")
    else:
        await interaction.response.send_message("No participants, re-launch of the draw completed without a winner.", ephemeral=True)

@bot.slash_command(name="delete", description="Delete a giveaway.")
async def supprimer(interaction: Interaction, message_id: str = nextcord.SlashOption(description="ID du message du giveaway à supprimer", required=True)):
    if not has_permission(interaction):
        await interaction.response.send_message("You are not authorised to use this command.", ephemeral=True)
        return

    message_id_int = int(message_id)
    if message_id_int not in giveaways and message_id_int not in finished_giveaways:
        await interaction.response.send_message("The giveaway with this ID does not exist.", ephemeral=True)
        return

    if message_id_int in giveaways:
        giveaways.pop(message_id_int)
    if message_id_int in finished_giveaways:
        finished_giveaways.pop(message_id_int)

    await interaction.response.send_message(f"The giveaway with the ID {message_id} has been deleted with success.")

@bot.slash_command(name="role", description="Configure the special role.")
async def configure_role(
    interaction: Interaction,
    role_name: str = nextcord.SlashOption(description="Name of the special role (for exemple 'gwperm')", required=True)
):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used on a server.", ephemeral=True)
        return

    if not interaction.user == interaction.guild.owner:
        await interaction.response.send_message("Only the server owner can configure the special role.", ephemeral=True)
        return

    role = nextcord.utils.get(interaction.guild.roles, name=role_name)
    if not role:
        await interaction.response.send_message(f"The role '{role_name}' does not exist on this server.", ephemeral=True)
        return

    config['special_role'] = role_name
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    await interaction.response.send_message(f"The special role has been configurate with success on '{role_name}'.", ephemeral=True)
 

@tasks.loop(seconds=60) 
async def check_giveaways():
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for message_id in list(finished_giveaways.keys()):
        await fin_giveaway(message_id)

@check_giveaways.before_loop
async def before_check_giveaways():
    await bot.wait_until_ready()

bot.run(config['token'])
