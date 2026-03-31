import json
import time
from datetime import datetime
import os

class BlackboxLogger:
    def __init__(self, log_file="nexus_debug.log"):
        self.log_file = log_file

    def log_event(self, agent_name, latency_ms, status, raw_data):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "latency": f"{latency_ms}ms",
            "status": status,
            "raw_payload": raw_data
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def self_healing_wrapper(raw_text, client, model="llama3-8b-8192"):
    import re
    clean_text = re.sub(r'```json\s?|```', '', raw_text).strip()
    
    try:
        return json.loads(clean_text), "SUCCESS"
    except json.JSONDecodeError:
        repair_prompt = (
            "Fix this broken JSON string. Return ONLY valid JSON. "
            f"\n\nBroken JSON:\n{raw_text}"
        )
        
        try:
            repair = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": repair_prompt}],
                temperature=0
            )
            repaired_text = re.sub(r'```json\s?|```', '', repair.choices[0].message.content).strip()
            return json.loads(repaired_text), "REPAIRED"
        except:
            return {}, "FAILED"
