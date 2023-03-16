from pydantic import BaseModel
import requests
import logging

TITLE_LIMIT = 140  # Spreaker limit
ELLIPSIS = "..."


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.url = config["url"]
        self.token = config["token"]
        self.show_id = config["show_id"]

    def upload(self, title, audio):
        response = self.requests.post(
            f"{self.url}/v2/shows/{self.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            files=[("media_file", ("audio.mp3", audio, "audio/mp3"))],
            data={"title": truncate_episode_title(title)},
        )


def truncate_episode_title(title):
    if len(title) > TITLE_LIMIT:
        return title[: TITLE_LIMIT - len(ELLIPSIS)] + ELLIPSIS
    return title
