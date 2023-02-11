from fastapi import FastAPI
from api import tts
from api import spreaker
from api import models
import logging

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)


@app.post("/")
def generate_news(trigger: models.PubSubTrigger):
    attributes = split_attributes(trigger)

    tts_client = tts.Client(attributes["tts"])

    spreaker_client = spreaker.Client(attributes["spreaker"])

    spreaker_client.upload(
        title="Dummy Title",
        audio=tts_client.speak("Hello, World!"),
    )
    return {"message": "Hello, World!!"}


def split_attributes(trigger: models.PubSubTrigger):
    # { 'foo_bar_baz': 'qux' } => { 'foo': { 'bar_baz': 'qux' } }
    result = {}
    for key, value in trigger.message.attributes.dict().items():
        prefix, suffix = key.split("_", maxsplit=1)
        if prefix not in result:
            result[prefix] = {}
        result[prefix][suffix] = value
    return result


@app.get("/health")
def health():
    return True
