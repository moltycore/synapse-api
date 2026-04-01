import os
from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.solo_prompts import SOLO_SYSTEM

def process_solo(query: str, client=None):
    active_client = client or Groq(api_key=GROQ_KEY)
    
    try:
        completion = active_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SOLO_SYSTEM},
                {"role": "user", "content": query}
            ],
            temperature=0.8,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.7,
            presence_penalty=0.6
        )

        answer = completion.choices[0].message.content
        
        if not answer:
            return {"route": "SHORT", "answer": "Error: Null response from model"}

        return {"route": "SHORT", "answer": answer.strip()}

    except Exception as e:
        return {"route": "SHORT", "answer": f"Agent execution failure: {str(e)}"}
