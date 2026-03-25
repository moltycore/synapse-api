import os
from dotenv import load_dotenv

# Localde test ederken .env dosyasını okuması için. Render'da zaten env var.
load_dotenv() 

GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")
