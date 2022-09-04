from fastapi import FastAPI
from pydantic import BaseModel
from api import spreaker

app = FastAPI()


class NewsTrigger(BaseModel):
    spreaker: spreaker.Config


@app.post("/")
def generate_news(trigger: NewsTrigger):
    spreaker_client = spreaker.Client(trigger.spreaker)
    spreaker_client.upload()
    return {"message": "Hello, World!!"}


@app.get("/health")
def health():
    return True
