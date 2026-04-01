import os
from dotenv import load_dotenv

load_dotenv()

# CORE PROVIDER KEYS
GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")

# HYBRID & PERSISTENCE LAYER KEYS
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PUTER_APP_ID = os.getenv("PUTER_APP_ID") # Used for other internal services

# SYNAPSE DASHBOARD SPECIFIC KEYS
PUTER_DASHBOARD_TOKEN = os.getenv("PUTER_DASHBOARD_TOKEN")
PUTER_DASHBOARD_APP_ID = os.getenv("PUTER_DASHBOARD_APP_ID") # The new App ID for Dashboard
