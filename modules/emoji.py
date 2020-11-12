import random

mapping = {
    'panic':  776515630546812978,
    'normal': 776515630626635796,
    'hyper':  776515630161068084,
    'empty':  776515630547468328,
    'angry':  776515630647214140
}

class Faces:
    def __init__(self, bot):
        self.bot = bot

    def get(self, face: str):
        id = mapping.get(face, None)
        if id is not None:
            return self.bot.get_emoji(id)
        else:
            return None

    def random(self):
        id = random.choice(list(mapping.values()))
        return self.bot.get_emoji(id)