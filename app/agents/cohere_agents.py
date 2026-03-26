import requests
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import BASDANISMAN_PREAMBLE

def get_basdanisman_res(soru, moderator_hukmu):
    url = "https://api.cohere.com/v1/chat"
    headers = {"Authorization": f"Bearer {COHERE_KEY}"}
    
    sarsici_mesaj = f"Kullanıcının Sorusu: '{soru}'\n\nModeratör Hükmü: '{moderator_hukmu}'\n\nSana verilen bu hükmü baz alarak kullanıcının sorusuna mutlak bir raconla cevap ver. Element uydurma."

    data = {
        "model": "command-r-plus-08-2024",
        "message": sarsici_mesaj,
        "preamble": BASDANISMAN_PREAMBLE,
        "temperature": 0.1
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        r.raise_for_status()
        return r.json().get("text", "Sentez başarısız.")
    except Exception as e:
        print(f"Başdanışman Hatası: {str(e)}")
        return "Başdanışman şu an mühür basamıyor."
