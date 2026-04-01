import json
import os
import requests
from datetime import datetime
from app.core.config import PUTER_DASHBOARD_APP_ID, PUTER_DASHBOARD_TOKEN

class BlackboxLogger:
    def __init__(self):
        self.token = PUTER_DASHBOARD_TOKEN
        self.app_id = PUTER_DASHBOARD_APP_ID
        self.base_url = "https://api.puter.com/v1/fs/write/Synapse-Dashboard/Archive"

    def _send(self, folder: str, payload: dict):
        if not self.token or not self.app_id:
            return False
            
        # Enforce Case-Sensitivity for Puter FS: 'Chats' or 'Logs'
        folder_name = folder.capitalize()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        url = f"{self.base_url}/{folder_name}/{timestamp}.json"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-puter-app-id": self.app_id, # Isolated Dashboard Identity
            "Content-Type": "application/json"
        }
        
        try:
            res = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload, ensure_ascii=False),
                timeout=5
            )
            return res.status_code == 200
        except Exception:
            return False

    def log_event(self, agent_name: str, latency_ms: int, status: str, raw_data: str):
        payload = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "latency": f"{latency_ms}ms",
            "status": status,
            "raw_payload": raw_data
        }
        return self._send("Logs", payload)

    def sync_to_puter(self, payload: dict, folder: str = "Chats"):
        return self._send(folder, payload)

def self_healing_wrapper(raw_text, client, model="llama3-8b-8192"):
    import re
    clean_text = re.sub(r'```json\s?|```', '', raw_text).strip()
    try:
        return json.loads(clean_text), "SUCCESS"
    except json.JSONDecodeError:
        if not client: return {}, "FAILED"
        repair_prompt = f"Fix this broken JSON string. Return ONLY valid JSON.\n\nBroken JSON:\n{raw_text}"
        try:
            repair = client.chat.completions.create(
                model=model, 
                messages=[{"role": "user", "content": repair_prompt}], 
                temperature=0
            )
            repaired_text = re.sub(r'```json\s?|```', '', repair.choices[0].message.content).strip()
            return json.loads(repaired_text), "REPAIRED"
        except Exception: 
            return {}, "FAILED"
