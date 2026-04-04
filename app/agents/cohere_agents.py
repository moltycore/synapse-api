import cohere
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import PRIME_SYSTEM

def get_prime_res(query: str, core_data: str, ghost_data: str, void_data: str) -> str:
    if not COHERE_KEY:
        return "Prime did not return a response."

    payload = (
        f"QUERY: '{query}'\n\n"
        f"CORE (REFINED): '{core_data}'\n\n"
        f"GHOST (VULNERABILITIES): '{ghost_data}'\n\n"
        f"VOID (DIRECTIVES): '{void_data}'\n\n"
    )

    try:
        co = cohere.ClientV2(api_key=COHERE_KEY)
        response = co.chat(
            model="command-r-plus-08-2024",
            messages=[
                {"role": "system", "content": PRIME_SYSTEM},
                {"role": "user", "content": payload}
            ],
            temperature=0.5,
            p=0.9,
            max_tokens=250,
            frequency_penalty=0.4,
            presence_penalty=0.3
        )
        return response.message.content[0].text
    except Exception as e:
        print(f"PRIME Critical Error: {str(e)}")
        return "Sistem hatası veya zaman aşımı oluştu."
