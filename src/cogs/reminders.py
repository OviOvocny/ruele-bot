import discord
import pendulum
from discord.ext import commands
from discord.ext import tasks
from modules.reminder_schedulers import Reminders as R

def is_valid_reminder (reminder):
    return reminder in [t.type for t in R.types]

class Reminders(commands.Cog):
    """Use these commands to register reminders for roles."""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.reminders = R()
        self.runner.start()

    def cog_unload(self):
        self.runner.cancel()

    # RUNNER ------------------------------------------------------------------

    @tasks.loop(hours=1, reconnect=True)
    async def runner(self):
        events = await self.reminders.upcoming()
        now = pendulum.now('UTC')
        current = list(filter(lambda e: e.datetime < now.add(minutes=59), events))
        for event in current:
            _, targets = await self.bot.db.hscan('reminders', match=f'{event.type}:*')
            for type_target, channel_role in targets:
                _, guild_id = type_target.split(':')
                channel_id, role_id = channel_role.split(':')

                guild = self.bot.get_guild(int(guild_id))
                channel = self.bot.get_channel(int(channel_id))
                role = discord.utils.get(guild.roles, id=int(role_id))

                msg = f'{role.mention} {event.message}'
                await channel.send(msg)


    @runner.before_loop
    async def before_reminders(self):
        await self.bot.wait_until_ready()
        now = pendulum.now('UTC')
        the_hour = now.at(now.hour + 1)
        print(f'Reminders starting at {the_hour}')
        await discord.utils.sleep_until(the_hour)



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
        await self.bot.db.hset('reminders', f'{reminder}:{guild.id}', f'{channel.id}:{role.id}')
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
        result = await self.bot.db.hdel('reminders', f'{reminder}:{guild.id}')

        if result == 0:
            await ctx.send('This reminder type wasn\'t registered here. My work here is done!')
        else:
            await ctx.send('Okay, I removed the reminder registration.')

    # LIST ALL ----------------------------------------------------------------

    @commands.command('reminders',
        brief='See available reminders and registered roles',
        help='I\'ll list all available reminders and the roles within your guild registered to receive them, if any.'
    )
    async def list_reminders(self, ctx):
        guild = ctx.message.guild
        rtypes = {r.type: r(0).description() for r in R.types}
        rroles = {}
        for rtype in rtypes.keys():
            val: str = await self.bot.db.hget('reminders', f'{rtype}:{guild.id}')
            if val:
                role_id = val.split(':')[1]
                role = discord.utils.get(guild.roles, id=int(role_id))
                rroles[rtype] = role.name

        msg = '\n\n'.join([f'__{t}__ ({rroles.get(t, "no role")})\n*{d}.*' for t,d in rtypes.items()])
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Reminders(bot))
