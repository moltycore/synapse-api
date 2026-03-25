# app/core/config.py
import os
from dotenv import load_dotenv

# Localde test ederken .env dosyasını okuması için. Render'da zaten env var.
load_dotenv() 

GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")

# YENİ HİBRİT YAPI ANAHTARLARI
# OpenRouter (openrouter/free rotası için) ve Puter (Yedek)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PUTER_APP_ID = os.getenv("PUTER_APP_ID")
