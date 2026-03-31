import os
from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.solo_prompts import SOLO_SYSTEM

# Default client as fallback
default_client = Groq(api_key=GROQ_KEY)

def process_solo(query: str, client=None, model="llama-3.3-70b-versatile"):
    # Use repair_client from engine if provided, else fallback to default
    active_client = client if client else default_client
    
    try:
        response = active_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SOLO_SYSTEM},
                {"role": "user", "content": query}
            ],
            max_tokens=250,
            temperature=0.4 
        )

        answer = response.choices[0].message.content.strip()
        
        if not answer:
            return {"route": "SHORT", "answer": "Model sustu, promptu kontrol et."}

        return {
            "route": "SHORT", 
            "answer": answer
        }

    except Exception as e:
        print(f"Solo Agent Detail Error: {e}")
        return {
            "route": "SHORT", 
            "answer": f"Solo engine failure: {str(e)}"
        }
