from datetime import datetime
from zoneinfo import ZoneInfo
import random

from core.generator import generate_plaintext_message

# Keep original behavior: generate message.txt when the module is run/imported.
# This file is intentionally small and continues to work as before but delegates
# to core.generator so future improvements are centralized.

def wish():
    generate_plaintext_message()


wish()
