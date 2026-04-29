from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.routes import router
from limiter import limiter

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
