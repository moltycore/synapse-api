import groq
from app.core.config import GROQ_KEY
from app.prompts.solo_prompts import SOLO_SYSTEM

client = groq.Client(api_key=GROQ_KEY)

def process_solo(soru):
    """
    Solo modu seçildiyse doğrudan kıdemli uzman cevabını üretir.
    'route': 'SHORT' dönmeye devam ediyoruz ki mevcut API/Frontend akışı patlamasın.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SOLO_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=150, # Uzman cevabı için ideal alan
            temperature=0.4 
        )

        answer = response.choices[0].message.content.strip()
        
        return {
            "route": "SHORT", 
            "answer": answer
        }

    except Exception as e:
        print(f"Solo Hatası: {e}")
        return {
            "route": "SHORT", 
            "answer": "Şu an cevap veremiyorum, sistemde bir pürüz var."
        }
