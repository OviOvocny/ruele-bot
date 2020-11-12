import discord
import shelve

async def manage_reaction(bot, payload, added: bool):
    if payload.user_id == bot.user.id:
        return

    with shelve.open('watched_messages') as wm:
        if not str(payload.message_id) in wm:
            return

        messageID = payload.message_id
        roleID = wm[str(messageID)]
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, id=roleID)
        member = discord.utils.get(guild.members, id=payload.user_id)

        if added:
            await member.add_roles(role)
        else:
            await member.remove_roles(role)