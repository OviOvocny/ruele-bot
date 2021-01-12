import json
import random
from asyncio import sleep
import discord
from discord.ext import commands
from modules.emoji import Faces

CHI = 349324050650365953
OVI = 399106406026051597

async def send_fortune(ctx, data):
    chi = ctx.message.author.id == CHI
    source = 'krautunes' if chi and random.random() < .5 else 'fortunes'
    await ctx.trigger_typing()
    await sleep(random.randrange(3,7))
    # chicken
    if discord.utils.get(ctx.message.author.roles, id=798618145223868437) is not None:
        await ctx.send('*Fuck Dizzy.*')
        return
    # -------
    await ctx.send('*'+random.choice(data[source])+'*')

class Fortune(commands.Cog):
    """No one shall escape the rabbit fortune cookies."""

    def __init__(self, bot):
        self.bot = bot
        self.faces = Faces(self.bot)
        with open('assets/fortune.json') as data:
            self.data = json.load(data)

    @commands.command('fortune',
        aliases=['cookie'],
        brief='Care for a cookie?',
        help='No one shall escape the rabbit fortune cookies.'
    )
    async def fortune(self, ctx):
        preface = random.choice(self.data['prefaces'])
        guild_name = ctx.message.guild.name if ctx.message.guild else 'Orbis'
        intro = preface.format(
            guild=guild_name
        )
        await ctx.trigger_typing()
        await sleep(1)
        await ctx.send(intro)
        #
        await ctx.trigger_typing()
        await sleep(random.randrange(1,2))
        await ctx.send(random.choice(self.data['transitions']) + ' ' + str(self.faces.random()))
        #
        await send_fortune(ctx, self.data)

    @commands.command('fortune_quick', 
        hidden=True
    )
    async def fortune_quick(self, ctx):
        await ctx.send('Let\'s crack this open!')
        await send_fortune(ctx, self.data)
        

def setup(bot):
    bot.add_cog(Fortune(bot))
