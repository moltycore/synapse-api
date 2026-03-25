import requests
from app.core.config import HF_KEY
from app.prompts.nexus_prompts import SME_SYSTEM

def get_sme_res(soru):
    url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    payload = {
        "inputs": f"Sistem: {SME_SYSTEM}\nSoru: {soru}", 
        "parameters": {"max_new_tokens": 80}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        return r.json()[0].get("generated_text", "Teknik veri alınamadı.").split("Cevap:")[-1].strip()
    except:
        return "SME şu an çevrimdışı."
