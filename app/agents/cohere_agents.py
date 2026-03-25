import requests
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import BASDANISMAN_PREAMBLE

def get_basdanisman_res(moderator_hukmu):
    url = "https://api.cohere.com/v1/chat"
    headers = {"Authorization": f"Bearer {COHERE_KEY}"}
    data = {
        "model": "command-r-plus-08-2024",
        "message": moderator_hukmu,
        "preamble": BASDANISMAN_PREAMBLE
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r.json().get("text", "Sentez başarısız.")
    except Exception:
        return "Başdanışman çevrimdışı."
