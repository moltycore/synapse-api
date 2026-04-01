import json
import time
import os
from groq import Groq
from app.agents.solo_agent import process_solo
from app.agents.moderator_agents import get_gatekeeper_res
from app.agents.groq_agents import get_core_res, get_ghost_res, get_void_res
from app.agents.cohere_agents import get_prime_res # Updated: Professional terminology
from app.utils.blackbox_logger import BlackboxLogger, self_healing_wrapper

REPAIR_KEY = os.getenv("REPAIR_GROQ_API_KEY")
repair_client = Groq(api_key=REPAIR_KEY) if REPAIR_KEY else None
logger = BlackboxLogger()

def run_nexus_protocol_stream(query: str, mode: str = "nexus"):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        return f"data: {payload}\n\n"

    # --- SOLO MODE EXECUTION ---
    if mode == "solo":
        yield emit("status", "solo")
        try:
            solo_output = process_solo(query, client=repair_client)
            result = solo_output.get("answer", "Solo engine failure.")
        except Exception:
            result = "Solo engine critical failure."

        yield emit("done", {
            "route": "SHORT", 
            "core_data": "Solo analysis active.", 
            "ghost_data": "N/A", 
            "void_data": "N/A",
            "prime_result": result
        })
        return

    # --- NEXUS PROTOCOL EXECUTION ---
    
    # 1. Intent Classification (Gatekeeper)
    yield emit("status", "gatekeeper")
    intent = get_gatekeeper_res(query, client=repair_client)

    if intent == "APPROVE":
        yield emit("done", {
            "route": "SHORT",
            "core_data": "User approval detected.",
            "ghost_data": "N/A",
            "void_data": "N/A",
            "prime_result": "Protocol acknowledged. Proceeding."
        })
        return

    # 2. Skeleton Extraction (Core)
    yield emit("status", "core")
    start = time.time()
    raw_core = get_core_res(query)
    core_data, status = self_healing_wrapper(raw_core, repair_client)
    logger.log_event("CORE", int((time.time() - start) * 1000), status, raw_core)

    # 3. Vulnerability Audit (Ghost)
    yield emit("status", "ghost")
    start = time.time()
    raw_ghost = get_ghost_res(json.dumps(core_data))
    ghost_data, status = self_healing_wrapper(raw_ghost, repair_client)
    logger.log_event("GHOST", int((time.time() - start) * 1000), status, raw_ghost)

    # 4. Directive Generation (Void)
    yield emit("status", "void")
    start = time.time()
    raw_void = get_void_res(json.dumps(core_data), json.dumps(ghost_data))
    void_data, status = self_healing_wrapper(raw_void, repair_client)
    logger.log_event("VOID", int((time.time() - start) * 1000), status, raw_void)

    # 5. Core Refinement
    yield emit("status", "core_refine")
    final_core = get_core_res(query, context=json.dumps(void_data))

    # 6. Final Authority (Prime)
    yield emit("status", "prime")
    try:
        # Pass full technical payload for synthesis
        prime_result = get_prime_res(
            query, 
            final_core, 
            json.dumps(ghost_data), 
            json.dumps(void_data)
        )
    except Exception:
        prime_result = "Prime synthesis critical failure."

    # Final Payload Emission
    yield emit("done", {
        "route": "COMPLEX",
        "core_data": json.dumps(core_data), 
        "ghost_data": json.dumps(ghost_data), 
        "void_data": json.dumps(void_data), 
        "prime_result": prime_result
    })
