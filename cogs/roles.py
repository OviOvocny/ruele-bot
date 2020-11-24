import shelve
import discord
from discord.ext import commands
from modules.utils import get_local_roles

class Roles(commands.Cog):
    """Use these commands to help manage roles in this guild."""

    def __init__(self, bot):
        self.bot = bot

    # MANAGE ROLES --------------------------------------------------------------

    @commands.command('manage-role', 
        aliases=['manage'],
        brief='Make a role self-assignable via reactions',
        help='I\'ll create a message with reaction for self-assigning a role. Members can add or remove the role by clicking the reaction. Deleting the message removes the role from my list of managed roles.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def manage_roles(self, ctx, *, role: discord.Role):
        await ctx.message.delete()
        msg = await ctx.send(f'Heirs of *{ctx.message.guild.name}*, click the reaction to add or remove the **{role.name}** role.')
        await msg.add_reaction('✅')
        with shelve.open('watched_messages', writeback=True) as wm:
            wm[str(msg.id)] = role.id

    @manage_roles.error
    async def manage_roles_err(self, ctx, err):
        if isinstance(err, commands.MissingPermissions):
            await ctx.send('Sorry, but you need to have permission to manage roles in this guild.')

    # LIST ROLES --------------------------------------------------------------

    @commands.command('list-roles', 
        aliases=['roles'],
        brief='Show roles managed by me',
        help='I\'ll list roles that I manage in this guild via reactions on messages that I create when instructed with the manage-role command.'
    )
    @commands.guild_only()
    async def list_roles(self, ctx):
        roles = []
        with shelve.open('watched_messages') as wm:
            roles = [role.name for role in get_local_roles(ctx.message.guild, wm.values())]
        nl = '\n'
        if len(roles) == 0:
            await ctx.send('Nothing in this guild yet…')
        else:
            await ctx.send(f'I manage these roles on *{ctx.message.guild.name}*:{nl}**{nl.join(roles)}**')

def setup(bot):
    bot.add_cog(Roles(bot))