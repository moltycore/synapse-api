import os
from dotenv import load_dotenv

load_dotenv()

# CORE KEYS
GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")

# HYBRID & PERSISTENCE KEYS
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PUTER_APP_ID = os.getenv("PUTER_APP_ID")
PUTER_DASHBOARD_TOKEN = os.getenv("PUTER_DASHBOARD_TOKEN") # Internal Dashboard Master Key
