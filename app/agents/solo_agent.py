import os
from groq import Groq
from app.core.config import GROQ_KEY

def run_senior_agent(query: str, system_prompt: str, client=None):
    # Initialize client if not provided
    active_client = client or Groq(api_key=GROQ_KEY)
    
    try:
        completion = active_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.8,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.7,
            presence_penalty=0.6
        )

        result = completion.choices[0].message.content
        return result.strip() if result else "Error: Null response from model"

    except Exception as e:
        return f"Agent execution failure: {str(e)}"
