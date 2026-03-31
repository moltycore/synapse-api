from app.prompts.nexus_prompts import GATEKEEPER_SYSTEM

def get_gatekeeper_res(query: str, client=None, model="llama-3.1-8b-instant") -> str:
    if not client:
        return "ANALYZE"
        
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": GATEKEEPER_SYSTEM},
                {"role": "user", "content": query}
            ],
            max_tokens=10,
            temperature=0.0
        )
        intent = response.choices[0].message.content.strip().upper()
        
        if intent not in ["APPROVE", "ANALYZE", "OBJECT"]:
            return "ANALYZE"
            
        return intent
        
    except Exception as e:
        print(f"Gatekeeper Error: {e}")
        return "ANALYZE"
