import requests
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import PRIME_SYSTEM

def get_yargic_res(query: str, core_data: str, ghost_data: str, void_data: str) -> str:
    url = "https://api.cohere.com/v1/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = (
        f"QUERY: '{query}'\n\n"
        f"CORE (REFINED): '{core_data}'\n\n"
        f"GHOST (VULNERABILITIES): '{ghost_data}'\n\n"
        f"VOID (DIRECTIVES): '{void_data}'\n\n"
    )

    data = {
        "model": "command-r-plus-08-2024",
        "message": payload,
        "preamble": PRIME_SYSTEM,
        "temperature": 0.2
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=40)
        r.raise_for_status()
        return r.json().get("text", "Prime did not return a response.")
    except Exception as e:
        print(f"PRIME Critical Error: {str(e)}")
        return "Sistem mühürleme hatası veya zaman aşımı oluştu. Teknik veriler korundu ancak nihai rapor üretilemedi."
