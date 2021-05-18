import shelve
import discord
from discord.ext import commands
from modules.utils import get_local_roles
from modules.checks import is_manager
from modules.emoji import Faces

class Roles(commands.Cog):
    """Use these commands to help manage roles in this guild."""

    def __init__(self, bot):
        self.bot = bot
        self.faces = Faces(bot)

    # DESIGNATE ROLES -----------------------------------------------------------

    @commands.command('manager-role',
        brief='Designate a role as the management role',
        help='The management role is able to use my role management commands. This command requires the manage roles permission.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def manager_role(self, ctx, *, role: discord.Role):
        await ctx.send(f'Ok, **{role.name}** is now the management role for *{ctx.message.guild.name}*.')
        with shelve.open('guild_managers', writeback=True) as gm:
            gm[str(ctx.message.guild.id)] = role.id

    @commands.command('member-role',
        brief='Designate a role as the guild membership role',
        help='The member role is used to distinguish in-game guild members from discord guests. This command requires the manage roles permission.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def member_role(self, ctx, *, role: discord.Role):
        await ctx.send(f'Ok, **{role.name}** is now the member role for *{ctx.message.guild.name}*.')
        with shelve.open('guild_members', writeback=True) as gm:
            gm[str(ctx.message.guild.id)] = role.id

    @commands.command('test-mgmt', hidden=True)
    @commands.check(is_manager)
    @commands.guild_only()
    async def test_mgmt(self, ctx):
        with shelve.open('guild_managers') as gm:
            await ctx.send(", ".join([str(a) for a in gm.values()]))

    # MANAGE MEMBERS ------------------------------------------------------------

    @commands.command('membership',
        aliases=['accept', 'kick'],
        brief='Toggle guild member role for a user',
        help='Using this command, managers can add or remove the designated *guild membership* role.'
    )
    @commands.check(is_manager)
    @commands.guild_only()
    async def membership(self, ctx, *, user: discord.Member):
        if user.bot:
            await ctx.send(f'{ctx.message.author.display_name}! {user.display_name} is a bot. {str(self.faces.get("angry"))}')
        else:
            guild_id = str(ctx.message.guild.id)
            with shelve.open('guild_members') as gm:
                if guild_id not in gm:
                    await ctx.send('No role set. Use the `member-role` command to designate a membership role first.')
                else:
                    role_id = gm[guild_id]
                    role = discord.utils.get(ctx.message.guild.roles, id=role_id)
                    user_role_ids = map(lambda x: x.id, user.roles)
                    if role_id in user_role_ids:
                        await user.remove_roles(role, reason=f'Kicked by {ctx.message.author.name}')
                        await ctx.send(f'Per {ctx.message.author.display_name}\'s request, {user.display_name} is no longer a member of the guild {str(self.faces.get("panic"))}')
                    else:
                        await user.add_roles(role, reason=f'Accepted by {ctx.message.author.name}')
                        await ctx.send(f'I added the {role.name} role on behalf of {ctx.message.author.display_name}. Welcome to the guild, {user.mention}! {str(self.faces.get("hyper"))}')

    @membership.error
    async def merr(self, ctx, err):
        member = discord.utils.get(ctx.message.guild.members, id=self.bot.user.id)
        print(member.guild_permissions)

    # MANAGE ROLES --------------------------------------------------------------

    @commands.command('manage-role', 
        aliases=['manage'],
        brief='Make a role self-assignable via reactions',
        help='I\'ll create a message with reaction for self-assigning a role. Members can add or remove the role by clicking the reaction. Deleting the message removes the role from my list of managed roles.'
    )
    @commands.check(is_manager)
    @commands.guild_only()
    async def manage_roles(self, ctx, *, role: discord.Role):
        await ctx.message.delete()
        msg = await ctx.send(f'Heirs of *{ctx.message.guild.name}*, click the reaction to add or remove the **{role.name}** role.')
        await msg.add_reaction('✅')
        with shelve.open('watched_messages', writeback=True) as wm:
            wm[str(msg.id)] = role.id

    @manage_roles.error
    async def manage_roles_err(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send('Sorry, but you need to have the management role in this guild.')

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