from openai import OpenAI
from app.core.config import DEEPSEEK_KEY
from app.prompts.nexus_prompts import MODERATOR_SYSTEM

ds_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")

def get_moderator_res(soru, sme, arastirma, denetci):
    p = f"Soru: {soru}\nVeriler:\nSME: {sme}\nAraştırma: {arastirma}\nDenetçi: {denetci}"
    try:
        res = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": MODERATOR_SYSTEM},
                {"role": "user", "content": p}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Moderatör hata verdi: {str(e)}"
