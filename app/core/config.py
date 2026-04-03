import os
import json
from dotenv import load_dotenv

load_dotenv()

# AI Provider Keys
GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# LangSmith / Tracing Config
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "Synapse-Nexus-Core")

# Firebase Config
FIREBASE_JSON_STR = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_CREDENTIALS = json.loads(FIREBASE_JSON_STR) if FIREBASE_JSON_STR else None
