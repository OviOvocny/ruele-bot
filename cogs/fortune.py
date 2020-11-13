import json
import random
from asyncio import sleep
import discord
from discord.ext import commands
from modules.emoji import Faces # pylint: disable=import-error

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
        intro = preface.format(
            guild=ctx.message.guild.name
        )
        await ctx.trigger_typing()
        await sleep(1)
        await ctx.send(intro)
        #
        await ctx.trigger_typing()
        await sleep(random.randrange(1,2))
        await ctx.send(random.choice(self.data['transitions']) + ' ' + str(self.faces.random()))
        #
        await ctx.trigger_typing()
        await sleep(random.randrange(3,7))
        await ctx.send('*'+random.choice(self.data['fortunes'])+'*')

    @commands.command('fortune_quick', 
        hidden=True
    )
    async def fortune_quick(self, ctx):
        await ctx.send('Let\'s crack this open!')
        await ctx.trigger_typing()
        await sleep(random.randrange(3,7))
        await ctx.send('*'+random.choice(self.data['fortunes'])+'*')

def setup(bot):
    bot.add_cog(Fortune(bot))