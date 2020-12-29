import shelve
import discord

def is_manager(ctx):
    guild_id = str(ctx.message.guild.id)
    author_roles = ctx.message.author.roles
    author_role_ids = map(lambda x: x.id, author_roles)
    with shelve.open('guild_managers') as gm:
        return gm[guild_id] in author_role_ids