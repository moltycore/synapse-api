import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import FIREBASE_CREDENTIALS

class BlackboxLogger:
    def __init__(self):
        if not firebase_admin._apps:
            if FIREBASE_CREDENTIALS:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
            else:
                raise ValueError("FIREBASE_CREDENTIALS missing in environment")
        self.db = firestore.client()

    def _send(self, collection: str, payload: dict):
        try:
            payload["timestamp"] = datetime.now().isoformat()
            self.db.collection("synapse_archive").document(collection).collection("payloads").add(payload)
            return True
        except Exception:
            return False

    def log_event(self, agent_name: str, latency_ms: int, status: str, raw_data: str):
        payload = {
            "agent": agent_name,
            "latency": f"{latency_ms}ms",
            "status": status,
            "raw_payload": raw_data
        }
        return self._send("logs", payload)

    def sync_to_firebase(self, payload: dict, folder: str = "chats"):
        return self._send(folder.lower(), payload)

def self_healing_wrapper(raw_text, client, model="llama3-8b-8192"):
    import re
    clean_text = re.sub(r'```json\s?|```', '', raw_text).strip()
    try:
        return json.loads(clean_text), "SUCCESS"
    except json.JSONDecodeError:
        if not client: 
            return {}, "FAILED"
        
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
