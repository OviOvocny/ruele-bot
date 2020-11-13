import discord
import shelve

def config(key, val = None, collection = False, delete = False):
    with shelve.open('s_config') as cfg:
        if val:
            if collection and key in cfg:
                if val in cfg[key]:
                    if delete:
                        cfg[key].remove(val)
                    return
                cfg[key].append(val)
            else:
                cfg[key] = [val] if collection else val
        else:
            return cfg.get(key, None)

def get_local_roles(guild, id_collection):
    if not id_collection or len(id_collection) == 0:
        return []
    roles = []
    for role_id in id_collection:
        try:
            role = discord.utils.get(guild.roles, id=role_id)
            if role is not None:
                roles.append(role)
        except:
            continue
    return roles