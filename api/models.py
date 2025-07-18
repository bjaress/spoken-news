from pydantic import BaseModel
import typing

# internal representations


class SpreakerConfig(BaseModel):
    url: str
    token: str
    show_id: int
    title_limit: int
    age_limit: int
    publish_delay_minutes: int


class TtsConfig(BaseModel):
    api_key: str
    server: str
    length_limit: int
    intro: str
    outro: str


class WikipediaConfig(BaseModel):
    url: str
    headlines_page: str
    polite_delay: int


class Config(BaseModel):
    wikipedia: WikipediaConfig
    spreaker: SpreakerConfig
    tts: TtsConfig


class ArticleReference(BaseModel):
    title: str
    section: typing.Optional[str]
    featured: bool


class Headline(BaseModel):
    text: str
    articles: typing.List[ArticleReference]


class Article(BaseModel):
    summary: typing.List[str]
    permalink_id: int
    reference: ArticleReference


# external representations


class Attributes(BaseModel):
    spreaker_url: str
    spreaker_token: str
    spreaker_show_id: int
    spreaker_title_limit: int
    spreaker_age_limit: int
    spreaker_publish_delay_minutes: int
    tts_api_key: str
    tts_server: str
    tts_length_limit: int
    tts_intro: str
    tts_outro: str
    wikipedia_url: str
    wikipedia_headlines_page: str
    wikipedia_polite_delay: int


class NewsMessage(BaseModel):
    attributes: Attributes


class NewsTrigger(BaseModel):
    message: NewsMessage


class CleanupMessage(BaseModel):
    attributes: SpreakerConfig


class CleanupTrigger(BaseModel):
    message: CleanupMessage
