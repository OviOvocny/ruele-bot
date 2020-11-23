import shelve
import discord
from discord.ext import commands
from modules.utils import get_local_roles # pylint: disable=import-error
from modules.reminder_schedulers import Reminders as R # pylint: disable=import-error

def is_valid_reminder (reminder):
    return reminder in [t.type for t in R.types]

class Reminders(commands.Cog):
    """Use these commands to register reminders for roles."""

    def __init__(self, bot):
        self.bot = bot

    # REMIND ROLES ------------------------------------------------------------

    @commands.command('assign-reminder', 
        aliases=['remind'],
        brief='Register a role for reminders of a specific type in this channel',
        help='I\'ll send reminders of a given type to the specified role. The reminders will be sent to this channel.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def assign_reminder(self, ctx, role: discord.Role, *, reminder: str):
        if not is_valid_reminder(reminder):
            raise commands.CommandError('This type of reminder doesn\'t exist')

        guild = ctx.message.guild
        channel = ctx.message.channel
        with shelve.open('reminder_map', writeback=True) as rm:
            if not reminder in rm:
                print('adding type')
                rm[reminder] = {}
            if not guild.id in rm[reminder]:
                print('adding guild')
                rm[reminder][guild.id] = None
            rm[reminder][guild.id] = (channel.id, role.id)
            print('SET')
            print(rm[reminder][guild.id])

        await ctx.send(f'Okay, I\'ll send periodic **{reminder}** reminders to this channel for the **{role.name}** role.')

    @assign_reminder.error
    async def assign_reminder_err(self, ctx, err):
        if isinstance(err, commands.CommandError):
            await ctx.send(err.message)
        if isinstance(err, commands.MissingPermissions):
            await ctx.send('Sorry, but you need to have permission to manage roles in this guild.')

    # REMOVE ------------------------------------------------------------------

    @commands.command('remove-reminder', 
        brief='Remove reminder type registration from guild',
        help='I\'ll unregister this guild from receiving reminders of the given type.'
    )
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def remove_reminder(self, ctx, *, reminder: str):
        if not is_valid_reminder(reminder):
            raise commands.CommandError('This type of reminder doesn\'t exist')

        guild = ctx.message.guild
        with shelve.open('reminder_map', writeback=True) as rm:
            print(rm.keys())
            print(rm[reminder].keys())
            if not reminder in rm or not guild.id in rm[reminder]:
                await ctx.send('This reminder type wasn\'t registered here. My work here is done!')
            else:
                del rm[reminder][guild.id]
                await ctx.send('Okay, I removed the reminder registration.')

    # SHOW NEXT ---------------------------------------------------------------

    @commands.command('upcoming', 
        brief='Get closest reminder info',
        help='I\'ll show details for the closest upcoming reminder and whether your guild is registered to receive it.'
    )
    async def upcoming_reminder(self, ctx):
        guild = ctx.message.guild
        event = R().next_event()

        with shelve.open('reminder_map') as rm:
            registered = True
            role = None
            if guild is None or not event.type in rm or not guild.id in rm[event.type]:
                registered = False
            else:
                _, role_id = rm[event.type][guild.id]
                role = discord.utils.get(guild.roles, id=role_id)


            info = f'Next up is **{event.title}**, scheduled for {event.datetime.format("dddd, MMMM DD, hh:mm")} UTC.'
            reg = 'You can only get reminders via a role in servers.'
            if guild is not None:
                reg = f'The **{role.name}** role is registered for {event.type} reminders.' if registered else f'You can register a role for {event.type} reminders using `:remind`.'

            await ctx.send(f'{info}\n*{event.detail}*\n{reg}')

def setup(bot):
    bot.add_cog(Reminders(bot))