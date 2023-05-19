from pydantic import BaseModel
import requests
import logging
import datetime as dt

import api.similar as similar

ELLIPSIS = "..."


class Client:
    def __init__(self, config, requests=requests, first_unknown=similar.first_unknown):
        self.requests = requests
        self.config = config
        self.first_unknown = first_unknown

    def upload(self, title, audio):
        response = self.requests.post(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
            files=[("media_file", ("audio.mp3", audio, "audio/mp3"))],
            data={"title": self.truncate_episode_title(title)},
        )

    def _existing_episodes(self):
        response = self.requests.get(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
            params={"filter": "editable", "sorting": "oldest"},
        )
        return response.json()["response"]["items"]

    def fresh_headline(self, headlines):
        episodes = [episode["title"] for episode in self._existing_episodes()]
        # in current Python versions, dicts are ordered
        potential_episodes = {
            self.truncate_episode_title(h.text): h for h in reversed(headlines)
        }

        return potential_episodes.get(
            self.first_unknown(list(potential_episodes.keys()), episodes)
        )

    def truncate_episode_title(self, title):
        if len(title) > self.config.title_limit:
            return title[: self.config.title_limit - len(ELLIPSIS)] + ELLIPSIS
        return title

    def cleanup(self, now):
        for episode in self._existing_episodes():
            published_at = dt.datetime.strptime(
                episode["published_at"], "%Y-%m-%d %H:%M:%S"
            )
            episode_id = episode["episode_id"]
            if published_at < now - dt.timedelta(days=self.config.age_limit):
                self.requests.delete(
                    f"{self.config.url}/v2/episodes/{episode_id}",
                    headers={
                        "Authorization": f"Bearer {self.config.token}",
                    },
                )
