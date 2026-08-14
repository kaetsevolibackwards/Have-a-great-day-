"""Message generator utilities for Stuff.

This module provides a simple, reusable generator that produces Message
instances. It is intentionally small and uses the standard library.
"""
from __future__ import annotations

import random
import uuid
from typing import List

from core.messages import Message
from core.time import now_timestamp
from core.config import JSON_VERSION, SERVER_ID

# Keep the same facts as the original Stuff/main.py to preserve behavior.
FACTS: List[str] = [
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
    "Butterflies taste with their feet.",
]


def generate_fact() -> str:
    return random.choice(FACTS)


def generate_message(msg_type: str = "fact") -> Message:
    """Return a Message dataclass instance with a unique id and timestamp.

    The function is deterministic in shape but random in content for the
    `fact` type so it can safely replace the original main.py behavior.
    """
    content = ""
    if msg_type == "fact":
        content = generate_fact()
    elif msg_type == "greeting":
        content = "Have a great day!"
    else:
        # fallback to a short system message
        content = f"[{msg_type}]"

    msg = Message(
        version=JSON_VERSION,
        id=str(uuid.uuid4()),
        type=msg_type,
        timestamp=now_timestamp(),
        server_id=SERVER_ID,
        message=content,
    )
    return msg
