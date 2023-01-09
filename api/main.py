from fastapi import FastAPI
from api import tts
from api import spreaker
from api import models

import pydub.generators as pdgen

app = FastAPI()


@app.post("/")
def generate_news(trigger: models.PubSubTrigger):
    attributes = split_attributes(trigger)

    tts_client = tts.Client(attributes["tts"])
    tts_client.speak("words")

    spreaker_client = spreaker.Client(attributes["spreaker"])

    spreaker_client.upload(
        title="Dummy Title",
        audio=pdgen.Sine(261.63).to_audio_segment().export(format="mp3"),
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
