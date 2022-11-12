from pydantic import BaseModel
import requests


class Config(BaseModel):
    url: str
    token: str
    show_id: int


class Client:
    def __init__(self, config: Config, requests=requests):
        self.config = config
        self.requests = requests

    def upload(self):
        self.requests.post(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
        )
