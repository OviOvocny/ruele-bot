import random
import re


greetings_in = ['hi', 'hello', 'yo', 'hey', 'heyo', 'greetings', 'good morning', 'good afternoon', 'good evening', 'sup', 'salutations', 'welcome']
greetings_out = ['hi', 'hello', 'yo', 'hey', 'greetings']

def greet():
    return random.choice(greetings_out).capitalize()

def is_greeted(string):
    regexes = '(?:%s)' % '|'.join([r'\b%s\b' % g for g in greetings_in])
    return bool(re.search(regexes, string, re.I))

def is_sailor_moon_meme(string):
    regex = 'you didn\'?t do anything'
    return bool(re.search(regex, string, re.I))
