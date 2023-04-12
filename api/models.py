from pydantic import BaseModel
import typing

# internal representations


class SpreakerConfig(BaseModel):
    url: str
    token: str
    show_id: int


class TtsConfig(BaseModel):
    api_key: str
    server: str


class WikipediaConfig(BaseModel):
    url: str
    headlines_page: str


class Config(BaseModel):
    wikipedia: WikipediaConfig
    spreaker: SpreakerConfig
    tts: TtsConfig


class Headline(BaseModel):
    text: str


# external representations


class Attributes(BaseModel):
    spreaker_url: str
    spreaker_token: str
    spreaker_show_id: int
    tts_api_key: str
    tts_server: str
    wikipedia_url: str
    wikipedia_headlines_page: str


class Message(BaseModel):
    attributes: Attributes


class PubSubTrigger(BaseModel):
    message: Message
