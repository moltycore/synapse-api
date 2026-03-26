import requests
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import BASDANISMAN_PREAMBLE

def get_basdanisman_res(moderator_hukmu):
    url = "https://api.cohere.com/v1/chat"
    headers = {"Authorization": f"Bearer {COHERE_KEY}"}
    
    data = {
        "model": "command-r-plus-08-2024",
        "message": f"Şu konsey hükmünü al, kendi mutlak kararın gibi mühürle ve racon kes: {moderator_hukmu}",
        "preamble": BASDANISMAN_PREAMBLE,
        "temperature": 0.1 # 0.1 demek: "Sıfır yaratıcılık, sadece emredileni kusursuz yap" demektir.
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        r.raise_for_status()
        return r.json().get("text", "Sentez başarısız.")
    except Exception as e:
        print(f"Başdanışman Hatası: {str(e)}")
        return "Başdanışman şu an mühür basamıyor."
