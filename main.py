# No one shall escape the rabbit fortune cookies. 

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

from modules.utils import config, get_local_roles
from modules.manage_reaction import manage_reaction
from modules.emoji import Faces

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(':'), intents=intents)
faces = Faces(bot)

bot.load_extension('cogs.roles')
bot.load_extension('cogs.fortune')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CommandNotFound):
        if bot.user in ctx.message.mentions:
            await ctx.send(faces.random())
        return
    await ctx.send(str(faces.get('panic')) + ' Sorry, I think I\'m lost… \n' + str(err))

# CONFIG --------------------------------------------------------------------



# MANAGE ROLES --------------------------------------------------------------

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

# SEND ANYTHING------------------------------------------------------------

@bot.command('send', hidden=True)
@commands.is_owner()
async def send_msg(ctx, channel: discord.TextChannel, *, msg: str):
    await channel.send(msg)

# SAY HI (?) --------------------------------------------------------------

from modules.keknlp import is_greeted, greet
from asyncio import sleep
from random import randrange

@bot.listen()
async def on_message(message):
    # Mentioned - send face
    # if bot.user in message.mentions:
    #     await message.channel.send(faces.random())
    # Greeting
    if not bot.user in message.mentions and len(message.mentions) > 0 and is_greeted(message.content):
        await sleep(randrange(5,10))
        await message.channel.trigger_typing()
        await sleep(1)
        await message.channel.send(greet() + '! ' + str(faces.get('hyper')))
    if '🥠' in message.content:
        await message.add_reaction(faces.get('hyper'))
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('fortune_quick'))


# -------------------------------------------------------------------------

bot.run(os.environ.get('RUELE_TOKEN'))
