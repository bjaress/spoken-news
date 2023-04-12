import fastapi as fa
import typing as tp

from api import tts
from api import spreaker
from api import models
from api import wikipedia
import logging

app = fa.FastAPI()
logging.basicConfig(level=logging.DEBUG)

# Converts models.PubSubTrigger to models.Config
# Does not assume field names, but does assume a naming convention with
# two-part names.
def decompose_attributes(trigger: models.PubSubTrigger):
    attributes = trigger.message.attributes
    parts = {}
    for name, structure in models.Config.__fields__.items():
        subparts = {}
        constructor = structure.type_
        for subname in constructor.__fields__.keys():
            subparts[subname] = getattr(attributes, f"{name}_{subname}")
        parts[name] = constructor(**subparts)
    return models.Config(**parts)


class Clients:
    def __init__(
        self, config: tp.Annotated[models.Config, fa.Depends(decompose_attributes)]
    ):
        self.wikipedia = wikipedia.Client(config.wikipedia)
        self.tts = tts.Client(config.tts)
        self.spreaker = spreaker.Client(config.spreaker)


@app.post("/")
def generate_news(clients: tp.Annotated[Clients, fa.Depends(Clients)]):

    headlines = clients.wikipedia.headlines()
    fresh_headline = clients.spreaker.fresh_headline(headlines)

    clients.spreaker.upload(
        title=fresh_headline.text,
        audio=clients.tts.speak(fresh_headline.text),
    )
    return {"message": fresh_headline.text}


@app.get("/health")
def health():
    return True
