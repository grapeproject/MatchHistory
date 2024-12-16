from fastapi import FastAPI, APIRouter
from api.endpoints.v1 import V1

app = FastAPI()

app.include_router(V1)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}
