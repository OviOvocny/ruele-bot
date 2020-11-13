import random

greetings = ['hi', 'hello', 'yo', 'hey', 'heyo', 'greetings', 'good morning', 'good afternoon', 'good evening', 'sup']
def greet():
    return random.choice(greetings).capitalize()
def is_greeted(string):
    return any(substring in string.lower() for substring in greetings)