import random

mapping = {
    'panic':  776515630546812978,
    'normal': 776515630626635796,
    'hyper':  776515630161068084,
    'empty':  776515630547468328,
    'angry':  776515630647214140,
    'sad': 799036426842800179,
    'smile': 799036464020324412
}

class Faces:
    def __init__(self, bot):
        self.bot = bot

    def get(self, face: str):
        eid = mapping.get(face, None)
        if eid is not None:
            return self.bot.get_emoji(eid)
        else:
            return None

    def random(self):
        eid = random.choice(list(mapping.values()))
        return self.bot.get_emoji(eid)
