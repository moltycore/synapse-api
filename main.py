from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Synapse API - The Nexus Protocol")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://synapse-nexus-ebon.vercel.app"],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

@app.get("/")
async def root():
    return {"status": "Synapse Online", "message": "Nexus Protocol Ready."}

app.include_router(router)
