from fastapi import FastAPI
from api import tts
from api import spreaker
from api import models
from api import wikipedia
import logging

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)


@app.post("/")
def generate_news(trigger: models.PubSubTrigger):
    attributes = split_attributes(trigger)

    wikipedia_client = wikipedia.Client(attributes["wikipedia"])
    tts_client = tts.Client(attributes["tts"])
    spreaker_client = spreaker.Client(attributes["spreaker"])

    headlines = wikipedia_client.headlines()
    logging.warn(headlines)
    message = spreaker_client.fresh_headline(headlines).text

    spreaker_client.upload(
        title=message,
        audio=tts_client.speak(message),
    )
    return {"message": message}


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
