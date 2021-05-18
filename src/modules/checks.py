async def is_manager(ctx):
    guild_id = ctx.message.guild.id
    author_roles = ctx.message.author.roles
    author_role_ids = list(map(lambda x: x.id, author_roles))
    manager_role_id = await ctx.bot.db.hget('manager_role', guild_id)
    if manager_role_id is None:
        return False
    return int(manager_role_id) in author_role_ids
