import os
import json
from dotenv import load_dotenv
from langsmith import Client, evaluate
from app.services.nexus_engine import run_nexus_protocol_stream

load_dotenv()

def process_eval_target(inputs: dict) -> dict:
    query = inputs.get("query", "")
    final_payload = None

    for chunk in run_nexus_protocol_stream(query, mode="nexus"):
        if "event: done" in chunk:
            raw_data = chunk.replace("data: ", "").strip()
            try:
                final_payload = json.loads(raw_data).get("data", {})
            except json.JSONDecodeError:
                return {"prime_result": "CRITICAL_ERROR: Parse Failure"}

    if not final_payload:
        return {"prime_result": "FAIL: Empty Payload"}

    return {"prime_result": final_payload.get("prime_result", "FAIL")}


if __name__ == "__main__":
    client = Client()
    target_dataset = "Nexus-Stress-Test"

    print(f"SYSTEM: Initiating evaluation sequence for [{target_dataset}]...")

    evaluate(
        process_eval_target,
        data=target_dataset,
        experiment_prefix="NEXUS_CORE_V1"
    )

    print("SYSTEM: Evaluation terminated. Matrix updated in LangSmith.")
