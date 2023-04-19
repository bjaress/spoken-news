from pydantic import BaseModel
import requests
import logging

ELLIPSIS = "..."


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.config = config

    def upload(self, title, audio):
        response = self.requests.post(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
            files=[("media_file", ("audio.mp3", audio, "audio/mp3"))],
            data={"title": self.truncate_episode_title(title)},
        )

    def fresh_headline(self, headlines):
        response = self.requests.get(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
            params={"filter": "editable"},
        )
        episodes = {e["title"] for e in response.json()["response"]["items"]}

        for candidate in reversed(headlines):
            if self.truncate_episode_title(candidate.text) not in episodes:
                return candidate

    def truncate_episode_title(self, title):
        if len(title) > self.config.title_limit:
            return title[: self.config.title_limit - len(ELLIPSIS)] + ELLIPSIS
        return title
