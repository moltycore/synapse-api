import json
import time
import os
from groq import Groq
from app.agents.solo_agent import process_solo
from app.agents.moderator_agents import get_gatekeeper_res
from app.agents.groq_agents import get_core_res, get_ghost_res, get_void_res
from app.agents.cohere_agents import get_prime_res
from app.utils.blackbox_logger import BlackboxLogger, self_healing_wrapper
from app.core.config import GROQ_KEY

REPAIR_KEY = os.getenv("REPAIR_GROQ_API_KEY")
repair_client = Groq(api_key=REPAIR_KEY) if REPAIR_KEY else None

_main_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
_gatekeeper_client = repair_client or _main_client

logger = BlackboxLogger()

def run_nexus_protocol_stream(query: str, mode: str = "nexus"):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        return f"data: {payload}\n\n"

    if mode == "solo":
        yield emit("status", "solo")
        try:
            solo_output = process_solo(query, client=repair_client)
            result = solo_output.get("answer", "Solo engine failure.")
        except Exception:
            result = "Solo engine critical failure."

        solo_payload = {
            "route": "SHORT", 
            "core_data": "Solo analysis active.", 
            "ghost_data": "N/A", 
            "void_data": "N/A",
            "prime_result": result
        }
        logger.sync_to_firebase({"query": query, **solo_payload}, folder="chats")
        yield emit("done", solo_payload)
        return

    yield emit("status", "gatekeeper")
    intent = get_gatekeeper_res(query, client=_gatekeeper_client)
    logger.log_event("GATEKEEPER", 0, intent, query)

    if intent == "APPROVE":
        yield emit("done", {
            "route": "SHORT",
            "core_data": "User approval detected.",
            "ghost_data": "N/A",
            "void_data": "N/A",
            "prime_result": "Protocol acknowledged. Proceeding."
        })
        return

    if intent == "OBJECT":
        yield emit("done", {
            "route": "SHORT",
            "core_data": "N/A",
            "ghost_data": "N/A",
            "void_data": "N/A",
            "prime_result": "Revision requested. Reframe your argument."
        })
        return

    yield emit("status", "core")
    start = time.time()
    raw_core = get_core_res(query)
    core_data, status = self_healing_wrapper(raw_core, repair_client)
    logger.log_event("CORE", int((time.time() - start) * 1000), status, raw_core)

    yield emit("status", "ghost")
    start = time.time()
    raw_ghost = get_ghost_res(json.dumps(core_data))
    ghost_data, status = self_healing_wrapper(raw_ghost, repair_client)
    logger.log_event("GHOST", int((time.time() - start) * 1000), status, raw_ghost)

    yield emit("status", "void")
    start = time.time()
    raw_void = get_void_res(json.dumps(core_data), json.dumps(ghost_data))
    void_data, status = self_healing_wrapper(raw_void, repair_client)
    logger.log_event("VOID", int((time.time() - start) * 1000), status, raw_void)

    yield emit("status", "core_refine")
    start = time.time()
    raw_final_core = get_core_res(query, context=json.dumps(void_data))
    final_core, status = self_healing_wrapper(raw_final_core, repair_client)
    logger.log_event("CORE_REFINE", int((time.time() - start) * 1000), status, raw_final_core)

    yield emit("status", "prime")
    try:
        prime_result = get_prime_res(
            query, 
            json.dumps(final_core), 
            json.dumps(ghost_data), 
            json.dumps(void_data)
        )
    except Exception:
        prime_result = "Prime synthesis critical failure."

    final_payload = {
        "route": "COMPLEX",
        "core_data": json.dumps(final_core), 
        "ghost_data": json.dumps(ghost_data), 
        "void_data": json.dumps(void_data), 
        "prime_result": prime_result
    }

    logger.sync_to_firebase({"query": query, **final_payload}, folder="chats")
    yield emit("done", final_payload)
