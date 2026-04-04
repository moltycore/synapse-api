import json
import threading
import pytz
import re
from datetime import datetime
from app.core.config import FIREBASE_CREDENTIALS

# Kütüphane kontrolü (2. versiyondan)
_firebase_available = False
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    _firebase_available = True
except ImportError:
    pass

class BlackboxLogger:
    def __init__(self):
        self.db = None
        if not _firebase_available or not FIREBASE_CREDENTIALS:
            print("WARNING: Firebase not available or credentials missing.")
            return

        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"[BlackboxLogger] Firebase init failed: {e}")

    def _background_write(self, collection: str, payload: dict):
        """Arka planda (Thread) Firebase'e yazar (1. versiyondan)"""
        if not self.db:
            return
        try:
            # İstanbul zaman dilimi (1. versiyondan)
            tz = pytz.timezone('Europe/Istanbul')
            payload["timestamp"] = datetime.now(tz).isoformat()
            
            self.db.collection("synapse_archive")\
                   .document(collection)\
                   .collection("payloads")\
                   .add(payload)
        except Exception as e:
            print(f"FIREBASE_SYNC_ERROR: {e}")

    def _send(self, collection: str, payload: dict):
        """Thread başlatıcı (1. versiyondan)"""
        if not self.db:
            return False
        thread = threading.Thread(target=self._background_write, args=(collection, payload))
        thread.daemon = True  # Uygulama kapanırken thread'in takılı kalmasını engeller
        thread.start()
        return True

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

def self_healing_wrapper(raw_text, client, model="llama-3.1-8b-instant"):
    """Güncel model ve temizleme mantığı (2. versiyondan)"""
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
