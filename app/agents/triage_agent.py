import groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import TRIAGE_SYSTEM

client = groq.Client(api_key=GROQ_KEY)

def check_complexity(soru):
    """
    Artık kategori ayrımı yapmaz. Triage modu seçildiyse doğrudan uzman cevabını üretir.
    'route': 'SHORT' dönmeye devam ediyoruz ki Nexus Engine akışı bozmasın.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=150, # Uzman cevabı için biraz daha alan tanıdık
            temperature=0.4 
        )

        answer = response.choices[0].message.content.strip()
        
        # Frontend ve Nexus Engine ile uyumluluk için 'SHORT' rotasını sabit bıraktık.
        return {
            "route": "SHORT", 
            "answer": answer
        }

    except Exception as e:
        print(f"Triage Hatası: {e}")
        return {
            "route": "SHORT", 
            "answer": "Şu an cevap veremiyorum, sistemde bir pürüz var."
        }
