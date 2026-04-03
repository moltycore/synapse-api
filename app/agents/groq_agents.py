from groq import Groq
from langsmith import traceable
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import CORE_SYSTEM, GHOST_SYSTEM, VOID_SYSTEM

client = Groq(api_key=GROQ_KEY)

@traceable(run_type="llm", name="CORE_Architect")
def get_core_res(query: str, context: str = "") -> str:
    prompt = f"Input: {query}\nContext: {context}"
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CORE_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.3, top_p=0.9, max_tokens=300,
        frequency_penalty=0.2, presence_penalty=0.1
    )
    return res.choices[0].message.content

@traceable(run_type="llm", name="GHOST_Auditor")
def get_ghost_res(core_response: str) -> str:
    prompt = f"CORE Draft:\n{core_response}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": GHOST_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.6, top_p=0.95, max_tokens=200,
        frequency_penalty=0.3, presence_penalty=0.4
    )
    return res.choices[0].message.content

@traceable(run_type="llm", name="VOID_Fixer")
def get_void_res(core_response: str, ghost_response: str) -> str:
    prompt = f"CORE Draft: {core_response}\nGHOST Findings: {ghost_response}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": VOID_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.2, top_p=0.9, max_tokens=200,
        frequency_penalty=0.2, presence_penalty=0.0
    )
    return res.choices[0].message.content
