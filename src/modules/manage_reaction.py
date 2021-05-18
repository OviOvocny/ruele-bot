import discord

async def manage_reaction(bot, payload, added: bool):
    if payload.user_id == bot.user.id:
        return

    roleID = await bot.db.hget('role_reactions', payload.message_id)

    if roleID is None:
        return

    guild = bot.get_guild(payload.guild_id)
    role = discord.utils.get(guild.roles, id=int(roleID))
    member = discord.utils.get(guild.members, id=payload.user_id)

    if added:
        await member.add_roles(role)
    else:
        await member.remove_roles(role)
