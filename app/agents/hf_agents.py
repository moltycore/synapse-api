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
        r = requests.post(url, headers=headers, json=payload, timeout=15) # Süreyi 15 sn yaptık, HF bazen geç uyanır
        
        # HTTP 200 harici bir kod dönerse direkt exception fırlatır
        r.raise_for_status() 
        
        json_resp = r.json()
        
        # HF hata mesajı döndüyse (dict formatında)
        if isinstance(json_resp, dict) and "error" in json_resp:
            hata = f"SME API Hatası: {json_resp['error']}"
            print(hata) # Render logs
            return hata
            
        # Başarılı senaryo (liste formatı)
        return json_resp[0].get("generated_text", "Teknik veri alınamadı.").split("Cevap:")[-1].strip()
        
    except Exception as e:
        # Hatanın ne olduğunu tam olarak yakalayıp paketliyoruz
        hata_mesaji = f"SME Çöktü. Hata türü: {type(e).__name__} - {str(e)}"
        
        # Eğer sunucudan bir cevap metni geldiyse onu da ekle
        if 'r' in locals() and hasattr(r, 'text'):
            hata_mesaji += f" | Detay: {r.text}"
            
        print(f"KRİTİK HATA [SME]: {hata_mesaji}") # Render loglarında kabak gibi parlasın
        return hata_mesaji
