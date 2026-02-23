import os
from dotenv import load_dotenv

# =======================
# Load keys from .env
# =======================
load_dotenv()
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
TOKEN_GPT = os.getenv("TOKEN_GPT")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
TELEGRAM_KYRYLO_ID = int(os.getenv("TELEGRAM_KYRYLO_ID", "0"))

ADMIN_CHAT_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_CHAT_IDS").split(",")
]

