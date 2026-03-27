import groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import TRIAGE_SYSTEM

def check_complexity(soru):
    client = groq.Client(api_key=GROQ_KEY)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Kapıdaki adam için en hızlı ve bedava model
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=60, # 3-5 kelime veya tek kelimelik etiketler için fazlasıyla yeterli
            temperature=0.3
        )
        res = response.choices[0].message.content.strip().upper()
        
        # Gelen cevabı parçalayıp vitese karar veriyoruz
        if "COMPLEX" in res:
            return {"route": "COMPLEX"}
        elif "MEDIUM" in res:
            return {"route": "MEDIUM"}
        elif "SHORT" in res:
            # "Naber lan | SHORT" gibi bir format bekliyoruz, "|" işaretinden öncesini al
            cevap = res.split("|")[0].strip() if "|" in res else res.replace("SHORT", "").strip()
            return {"route": "SHORT", "answer": cevap}
        else:
            # Eğer model kafayı yer de saçmalarsa, riske atma, en ağır yoldan gönder
            return {"route": "COMPLEX"}
            
    except Exception as e:
        print(f"Triage Hatası: {e}")
        return {"route": "COMPLEX"} # Hata olursa da mecburen konseyi topluyoruz
