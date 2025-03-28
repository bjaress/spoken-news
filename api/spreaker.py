from pydantic import BaseModel
import requests
import logging
import datetime as dt

import api.similar as similar

ELLIPSIS = "..."

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Client:
    def __init__(self, config, requests=requests, unknowns=similar.unknowns):
        self.requests = requests
        self.config = config
        self.unknowns = unknowns

    def upload(self, title, audio, description, now=None):
        if now is None:
            now = dt.datetime.now()
        publish_time = now + dt.timedelta(minutes=self.config.publish_delay_minutes)
        response = self.requests.post(
            f"{self.config.url}/v2/shows/{self.config.show_id}/episodes",
            headers={
                "Authorization": f"Bearer {self.config.token}",
            },
            files=[("media_file", ("audio.mp3", audio, "audio/mp3"))],
            data={
                "title": self.truncate_episode_title(title),
                "description": description,
                "auto_published_at": publish_time.strftime(DATETIME_FORMAT),
            },
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
        return next(self.fresh_headlines(headlines), None)

    def fresh_headlines(self, headlines):
        episodes = [episode["title"] for episode in self._existing_episodes()]
        # in current Python versions, dicts are ordered
        potential_episodes = {
            self.truncate_episode_title(h.text): h for h in reversed(headlines)
        }

        for unknown_episode in self.unknowns(list(potential_episodes.keys()), episodes):
            yield potential_episodes.get(unknown_episode)

    def truncate_episode_title(self, title):
        if len(title) > self.config.title_limit:
            return title[: self.config.title_limit - len(ELLIPSIS)] + ELLIPSIS
        return title

    def cleanup(self, now):
        for episode in self._existing_episodes():
            published_at = dt.datetime.strptime(
                episode["published_at"], DATETIME_FORMAT
            )
            episode_id = episode["episode_id"]
            if published_at < now - dt.timedelta(days=self.config.age_limit):
                self.requests.delete(
                    f"{self.config.url}/v2/episodes/{episode_id}",
                    headers={
                        "Authorization": f"Bearer {self.config.token}",
                    },
                )
