from typing import Optional
from fastapi import FastAPI

app = FastAPI()

@app.post("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return True
