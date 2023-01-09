from pydantic import BaseModel


class Attributes(BaseModel):
    spreaker_url: str
    spreaker_token: str
    spreaker_show_id: int
    tts_api_key: str
    tts_server: str


class Message(BaseModel):
    attributes: Attributes


class PubSubTrigger(BaseModel):
    message: Message
