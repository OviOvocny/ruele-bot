import os
import discord
from discord.ext import commands

import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='ruele.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

import shelve

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(':'), intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def manage(ctx, *, role: discord.Role):
    await ctx.message.delete()
    msg = await ctx.send(f'Heirs of {ctx.message.guild.name}, click the reaction to add or remove **{role.name}** role.')
    await msg.add_reaction('✅')
    with shelve.open('watched_messages') as wm:
        wm[str(msg.id)] = role.id

async def manage_reaction(payload, added: bool):
    if payload.user_id == bot.user.id:
        return

    with shelve.open('watched_messages') as wm:
        if not str(payload.message_id) in wm:
            return

        messageID = payload.message_id
        roleID = wm[str(messageID)]
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, id=roleID)
        member = discord.utils.get(guild.members, id=payload.user_id)

        if added:
            await member.add_roles(role)
        else:
            await member.remove_roles(role)

@bot.event
async def on_raw_reaction_add(payload):
    await manage_reaction(payload, True)

@bot.event
async def on_raw_reaction_remove(payload):
    await manage_reaction(payload, False)

@bot.event
async def on_raw_message_delete(payload):
    with shelve.open('watched_messages') as wm:
        if str(payload.message_id) in wm:
            del wm[str(payload.message_id)]


bot.run(os.environ.get('RUELE_TOKEN'))