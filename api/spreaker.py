from pydantic import BaseModel
import requests
import logging
from api import models


class Client:
    def __init__(self, config: models.Attributes, requests=requests):
        self.requests = requests
        self.url = config.spreaker_url
        self.token = config.spreaker_token
        self.show_id = config.spreaker_show_id

    def upload(self, title, audio):
        response = self.requests.post(
            f"{self.url}/v2/shows/{self.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            files=[("media_file", ("audio.mp3", audio, "audio/mp3"))],
            data={"title": title},
        )
        logging.info(f"Spreaker Request: {response.status_code}")
