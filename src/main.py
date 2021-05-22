# No one shall escape the rabbit fortune cookies.

import os
import atexit
import logging
from asyncio import sleep
from random import randrange, random
import aioredis

import discord
from discord.ext import commands
from discord_slash.client import SlashCommand
from constants import REDIS_PASS

from modules.manage_reaction import manage_reaction
from modules.emoji import Faces
# from modules.reminder_schedulers import Reminders
from modules.keknlp import is_greeted, greet, is_sailor_moon_meme, is_gun

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='logs/ruele.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(':'), intents=intents)
faces = Faces(bot)
slash = SlashCommand(bot, sync_commands=True)

bot.load_extension('cogs.roles')
bot.load_extension('cogs.fortune')
bot.load_extension('cogs.reminders')

async def on_exit():
    # pylint: disable=no-member
    print('Closing Redis pool...')
    bot.db.close()
    await bot.db.wait_closed()

@bot.event
async def on_ready():
    atexit.register(on_exit)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    status = discord.Status.do_not_disturb if 'DEVMODE' in os.environ else discord.Status.online
    print(status)
    await bot.change_presence(status=status)
    print('------')
    try:
        # Use the high-level interface.
        db_pool = await aioredis.create_redis_pool(
            "redis://storage",
            password=REDIS_PASS,
            encoding="utf-8"
        )
        setattr(bot, "db", db_pool)
        print('Redis pool open')
    except OSError:
        logger.error('Could not open database pool. Exiting!')
        exit()

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CommandNotFound):
        if bot.user in ctx.message.mentions:
            await ctx.send(faces.random())
        return
    await ctx.send(str(faces.get('panic')) + ' Sorry, I think I\'m lost… \n' + str(err))
    logger.error(err)

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
    # pylint: disable=no-member
    await bot.db.hdel('role_reactions', payload.message_id)

# SEND ANYTHING------------------------------------------------------------

@bot.command('send', hidden=True)
@commands.is_owner()
async def send_msg(_, channel: discord.TextChannel, *, msg: str):
    await channel.send(msg)

# SAY HI (?) --------------------------------------------------------------

@bot.listen()
async def on_message(message):
    # Greeting
    if not bot.user in message.mentions and message.author.id != bot.user.id and len(message.mentions) > 0 and is_greeted(message.content):
        await sleep(randrange(5,10))
        await message.channel.trigger_typing()
        await sleep(1)
        await message.channel.send(greet() + '! ' + str(faces.get('hyper')))
    # FORTUNE COOKIE!!!!!!!
    if '🥠' in message.content:
        await message.add_reaction(faces.get('hyper'))
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('fortune_quick'))
    # ...tuxedo mask
    if is_sailor_moon_meme(message.content):
        await sleep(1)
        await message.channel.send('https://media.giphy.com/media/aenAbxws6nvbO/giphy.gif')
    # Tagrage
    if message.mention_everyone:
        await sleep(randrange(1,3))
        await message.add_reaction(faces.get('angry'))
    # GUN
    if is_gun(message.content) and message.author.id != bot.user.id and random() < .7:
        KYU = 749710868689846453
        await sleep(1)
        await message.channel.trigger_typing()
        await sleep(randrange(1,2))
        await message.channel.send(bot.get_emoji(KYU))


# -------------------------------------------------------------------------

bot.run(os.environ.get('RUELE_TOKEN'))
