import typing
import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from slugify import slugify
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
        await self.bot.db.hset('manager_role', ctx.message.guild.id, role.id)
        await ctx.send(f'Ok, **{role.name}** is now the management role for *{ctx.message.guild.name}*.')

    @commands.command('member-role',
        brief='Designate a role as the guild membership role',
        help='The member role is used to distinguish in-game guild members from discord guests. This command requires the manage roles permission.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def member_role(self, ctx, *, role: discord.Role):
        await self.bot.db.hset('member_role', ctx.message.guild.id, role.id)
        await ctx.send(f'Ok, **{role.name}** is now the member role for *{ctx.message.guild.name}*.')

    # MANAGE MEMBERS ------------------------------------------------------------

    @commands.command('membership',
        aliases=['accept', 'kick'],
        brief='Toggle guild member role for a user',
        help='Using this command, managers can add or remove the designated *guild membership* role. Optionally add IGN for me to remember.'
    )
    @commands.check(is_manager)
    @commands.guild_only()
    async def membership(self, ctx, user: discord.Member, ign: typing.Optional[str]):
        if user.bot:
            await ctx.send(f'{ctx.message.author.display_name}! {user.display_name} is a bot. {str(self.faces.get("angry"))}')
        else:
            guild_id = str(ctx.message.guild.id)
            member_role_id = await self.bot.db.hget('member_role', guild_id)
            if member_role_id is None:
                await ctx.send('No role set. Use the `member-role` command to designate a membership role first.')
            else:
                role = discord.utils.get(ctx.message.guild.roles, id=int(member_role_id))
                user_role_ids = map(lambda x: x.id, user.roles)
                if int(member_role_id) in user_role_ids:
                    await self.bot.db.hdel('ign', user.id)
                    await user.remove_roles(role, reason=f'Kicked by {ctx.message.author.name}')
                    await ctx.send(f'Per {ctx.message.author.display_name}\'s request, {user.display_name} is no longer a member of the guild {str(self.faces.get("panic"))}')
                else:
                    if ign:
                        await self.bot.db.hset('ign', user.id, ign)
                    await user.add_roles(role, reason=f'Accepted by {ctx.message.author.name}')
                    await ctx.send(f'I added the {role.name} role on behalf of {ctx.message.author.display_name}. Welcome to the guild, {user.mention}! {str(self.faces.get("hyper"))}')

    @membership.error
    async def merr(self, ctx, err):
        member = discord.utils.get(ctx.message.guild.members, id=self.bot.user.id)
        print(member.guild_permissions)

    # MANAGE IGN ----------------------------------------------------------------

    @cog_ext.cog_slash(
        # guild_ids=[416262003070337034], # dev
        name='ign',
        description='Recall or set user\'s in-game name',
        options=[
            create_option(
                name='user',
                description='User whose name you want to look up or save',
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name='name',
                description='The in-game name to save',
                option_type=SlashCommandOptionType.STRING,
                required=False
            )
        ]
    )
    async def ign(self, ctx, user: discord.User, name: str = None):
        if name is None:
            stored = await self.bot.db.hget('ign', user.id)
            if stored is None:
                await ctx.send(f'I don\'t know {user.display_name}\'s IGN {str(self.faces.get("panic"))}', hidden=True)
            else:
                await ctx.send(f'{user.display_name} is {stored}.', hidden=True)
        else:
            await self.bot.db.hset('ign', user.id, name)
            await self.bot.db.hset('reverseign', slugify(name), user.id)
            await ctx.send(f'I\'ll remember {user.display_name} as {name}!', hidden=True)

    @cog_ext.cog_slash(
        # guild_ids=[416262003070337034], # dev
        name='whois',
        description='Find a Discord member by in-game name',
        options=[
            create_option(
                name='ign',
                description='In-game name you want to look up (case-insensitive)',
                option_type=SlashCommandOptionType.STRING,
                required=True
            )
        ]
    )
    async def whois(self, ctx, ign: str):
        stored = await self.bot.db.hget('reverseign', slugify(ign))
        if stored is None:
            await ctx.send(f'I don\'t know who {ign} is {str(self.faces.get("panic"))} (maybe they left)', hidden=True)
        else:
            print(dir(ctx))
            member = discord.utils.get(ctx.guild.members, id=int(stored))
            if not member:
                await ctx.send(f'I don\'t see {ign} in this server, so I can\'t give you a name {str(self.faces.get("sad"))}', hidden=True)
            await ctx.send(f'{ign} is {member.display_name} ({member.name}#{member.discriminator}) on Discord.', hidden=True)

    @commands.command('sync-ign-data', hidden=True)
    @commands.is_owner()
    async def sync_ign_data(self, ctx):
        await ctx.send('Scanning IGNs. You shouldn\'t need to do this again once completed.')
        _, mapping = await self.bot.db.hscan('ign')
        num_synced = 0
        for uid, ign in mapping:
            result = await self.bot.db.hsetnx('reverseign', slugify(ign), uid)
            num_synced += int(result)
        await ctx.send(f'IGN mapping complete. I synchronised {num_synced} names for reverse lookups. Try it out with `/whois <ign>`.')



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
        await self.bot.db.hset('role_reactions', msg.id, role.id)

    @manage_roles.error
    async def manage_roles_err(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send('Sorry, but you need to have the management role in this guild.')

def setup(bot):
    bot.add_cog(Roles(bot))