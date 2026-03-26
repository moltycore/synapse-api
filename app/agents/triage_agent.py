import groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import TRIAGE_SYSTEM

def check_complexity(soru):
    client = groq.Client(api_key=GROQ_KEY)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=50,
            temperature=0.7
        )
        res = response.choices[0].message.content.strip()
        # Eğer içinde COMPLEX geçmiyorsa basit yoldan devam et
        return {"is_complex": "COMPLEX" in res.upper(), "short_answer": res}
    except:
        return {"is_complex": True, "short_answer": ""}
