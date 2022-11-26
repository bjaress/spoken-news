from fastapi import FastAPI
from api import spreaker
from api import models

import pydub.generators as pdgen

app = FastAPI()


@app.post("/")
def generate_news(trigger: models.PubSubTrigger):
    spreaker_client = spreaker.Client(trigger.message.attributes)

    spreaker_client.upload(
        title="Dummy Title",
        audio=pdgen.Sine(261.63).to_audio_segment().export(format="mp3"),
    )
    return {"message": "Hello, World!!"}


@app.get("/health")
def health():
    return True
