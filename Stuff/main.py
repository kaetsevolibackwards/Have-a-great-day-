from datetime import datetime
from zoneinfo import ZoneInfo
import random

facts = [
    "Octopuses have three hearts.",
    "Bananas are berries, but strawberries aren't.",
    "A day on Venus is longer than a year on Venus.",
    "Honey can remain edible for an extremely long time.",
    "Sharks existed before trees.",
    "Wombat poop is cube-shaped.",
    "The Eiffel Tower can grow slightly taller in hot weather.",
    "Some turtles can breathe through their butts.",
    "Cows have best friends and can become stressed when separated.",
    "A group of flamingos is called a flamboyance.",
    "The shortest war in history lasted less than an hour.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "There are more possible games of chess than atoms in the observable universe.",
    "A bolt of lightning can be hotter than the surface of the Sun.",
    "Butterflies taste with their feet."
]


def wish():
    now = datetime.now(ZoneInfo("America/Chicago"))
    hour = now.hour

    if hour < 12:
        greeting = "Good morning. Have a great day"
    elif hour < 18:
        greeting = "Good afternoon. Have a great day"
    else:
        greeting = "Good evening. Have a great day"

    fact = random.choice(facts)

    message = f"{greeting}\n\nFun fact:\n{fact}"

    with open("message.txt", "w", encoding="utf-8") as file:
        file.write(message)


wish()