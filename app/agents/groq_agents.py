from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import ANALIZCI_SYSTEM, DENETCI_SYSTEM

client = Groq(api_key=GROQ_KEY)

def get_analizci_res(soru):
    # SME ve Araştırmacı tek bedende birleşti. Sadece konuyu veriyoruz, kendisi deşiyor.
    prompt = f"Analiz Edilecek Konu: {soru}"
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Ağır top burada çalışıyor
        messages=[
            {"role": "system", "content": ANALIZCI_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

def get_denetci_res(analiz_cevap):
    # Denetçi sadece Analizci'nin sunduğu veriyi parçalamaya odaklanır
    prompt = f"Analizci'nin Çıktısı:\n{analiz_cevap}"
    
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant", # Acımasız risk avcısı için hızlı model
        messages=[
            {"role": "system", "content": DENETCI_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content
