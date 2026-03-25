from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="Synapse API - The Nexus Protocol")

# Tarayıcı (Frontend) engeline takılmamak için kapıları açıyoruz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gelen tüm istekleri gişeye (routes.py) yönlendir
app.include_router(router)
