from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.solo_prompts import SOLO_SYSTEM
from app.utils.blackbox_logger import BlackboxLogger 

logger = BlackboxLogger()
default_client = Groq(api_key=GROQ_KEY)

def process_solo(query: str, client=None):
    active_client = client or default_client
    try:
        completion = active_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SOLO_SYSTEM},
                {"role": "user", "content": query}
            ],
            temperature=0.8, max_tokens=500, top_p=0.9,
            frequency_penalty=0.7, presence_penalty=0.6
        )
        answer = completion.choices[0].message.content
        if not answer:
            return {"route": "SHORT", "answer": "Error: Null response"}

        payload = {"route": "SHORT", "answer": answer.strip(), "query": query}
        logger.sync_to_firebase(payload, folder="chats")
        return payload

    except Exception as e:
        err_msg = f"Agent execution failure: {str(e)}"
        logger.log_event("SOLO_AGENT", 0, "CRITICAL_ERROR", err_msg)
        return {"route": "SHORT", "answer": err_msg}
