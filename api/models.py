from pydantic import BaseModel
import typing


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


class Headline(BaseModel):
    text: str
