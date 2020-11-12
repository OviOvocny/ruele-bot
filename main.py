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

from modules.manage_reaction import manage_reaction
from modules.emoji import Faces

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(':'), intents=intents)
faces = Faces(bot)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# MANAGE ROLES --------------------------------------------------------------

@bot.command('manage-role', aliases=['manage'])
async def manage_roles(ctx, *, role: discord.Role):
    await ctx.message.delete()
    msg = await ctx.send(f'Heirs of *{ctx.message.guild.name}*, click the reaction to add or remove the **{role.name}** role.')
    await msg.add_reaction('✅')
    with shelve.open('watched_messages') as wm:
        wm[str(msg.id)] = role.id

@bot.event
async def on_raw_reaction_add(payload):
    await manage_reaction(bot, payload, True)

@bot.event
async def on_raw_reaction_remove(payload):
    await manage_reaction(bot, payload, False)

@bot.event
async def on_raw_message_delete(payload):
    with shelve.open('watched_messages') as wm:
        if str(payload.message_id) in wm:
            del wm[str(payload.message_id)]

# LIST ROLES --------------------------------------------------------------

@bot.command('list-roles', aliases=['roles'])
async def list_roles(ctx):
    roles = []
    with shelve.open('watched_messages') as wm:
        for role_id in wm.values():
            try:
                role = discord.utils.get(ctx.message.guild.roles, id=role_id)
                roles.append(role.name)
            except:
                continue
    nl = '\n'
    if len(roles) == 0:
        await ctx.send('Nothing in this guild yet…')
    else:
        await ctx.send(f'I manage these roles on *{ctx.message.guild.name}*:{nl}**{nl.join(roles)}**')

# SEND ANYTHING------------------------------------------------------------

@bot.command('send')
async def send_msg(ctx, channel: discord.TextChannel, *, msg: str):
    await channel.send(msg)

# SAY HI (?) --------------------------------------------------------------

@bot.listen()
async def on_message(message):
    if bot.user in message.mentions:
        await message.channel.send(faces.random())


# -------------------------------------------------------------------------

bot.run(os.environ.get('RUELE_TOKEN'))
