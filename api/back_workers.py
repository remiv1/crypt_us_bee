from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur l'API FastAPI !"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    retour: Dict[str, Any] = {"item_id": item_id, 'q': q}
    return retour