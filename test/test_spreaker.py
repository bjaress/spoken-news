import unittest
import hamcrest as ham
import hypothesis as hyp
from unittest import mock
import datetime

import api.models as models
from api import spreaker

from requests.exceptions import HTTPError


class TestSpreaker(unittest.TestCase):
    def setUp(self):
        config = mock.MagicMock()
        config.url = "THE_URL"
        config.token = "THE_TOKEN"
        config.show_id = 0
        config.title_limit = 50
        config.publish_delay_minutes = 7
        self.config = config
        self.requests = mock.Mock()
        self.requests.get.return_value.json.return_value = episodes_with_titles([])
        self.unknowns = mock.Mock()
        self.client = spreaker.Client(
            config, requests=self.requests, unknowns=self.unknowns
        )

    def test_upload(self):
        now = datetime.datetime.strptime(
            "2000-01-01 00:00:00", spreaker.DATETIME_FORMAT
        )
        self.requests.post.assert_not_called()
        self.client.upload(
            title="THE_TITLE", audio=b"THE_AUDIO", description="THE_DESC", now=now
        )

        ham.assert_that(
            self.requests.post.call_args.args,
            ham.contains_exactly("THE_URL/v2/shows/0/episodes"),
        )
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entries(
                {
                    "headers": {
                        "Authorization": "Bearer THE_TOKEN",
                    },
                    # presence of files triggers the correct content-type
                    "files": [("media_file", ("audio.mp3", b"THE_AUDIO", "audio/mp3"))],
                    "data": ham.has_entries(
                        {
                            "title": "THE_TITLE",
                            "description": "THE_DESC",
                            "auto_published_at": f"2000-01-01 00:{self.config.publish_delay_minutes:02d}:00",
                        }
                    ),
                }
            ),
        )

    def test_fresh_headlines(self):
        fresh = models.Headline(text="THE_TITLE", articles=[])
        self.unknowns.return_value = iter([fresh.text])

        response = next(self.client.fresh_headlines([fresh]))

        self.requests.get.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            params={"filter": "editable", "sorting": "oldest"},
        )
        self.unknowns.assert_called_with([fresh.text], [])
        ham.assert_that(
            response, ham.equal_to(fresh), "The fresh headline should be chosen."
        )

    def test_fresh_headlines_multiple(self):
        headline_a = models.Headline(text="HEADLINE_A", articles=[])
        headline_b = models.Headline(text="HEADLINE_B", articles=[])
        headline_c = models.Headline(text="HEADLINE_C", articles=[])
        self.requests.get.return_value.json.return_value = episodes_with_titles(
            ["EPISODE_A", "EPISODE_D"]
        )
        self.unknowns.return_value = iter([headline_b.text])

        response = next(
            self.client.fresh_headlines([headline_a, headline_b, headline_c])
        )

        self.unknowns.assert_called_with(
            [headline_a.text, headline_b.text, headline_c.text],
            ["EPISODE_A", "EPISODE_D"],
        )
        ham.assert_that(
            response,
            ham.equal_to(headline_b),
            "The first unknown headline should be chosen.",
        )

    def test_fresh_headlines_truncated(self):
        headline = models.Headline(text=("long" * self.config.title_limit), articles=[])
        assert len(headline.text) > self.config.title_limit
        truncated = self.client.truncate_episode_title(headline.text)
        self.unknowns.return_value = iter([truncated])

        response = next(self.client.fresh_headlines([headline]))
        self.unknowns.assert_called_with([truncated], [])
        ham.assert_that(
            response,
            ham.equal_to(headline),
            "The first unknown headline should be chosen.",
        )

    def test_fresh_headlines_all_stale(self):
        stale = models.Headline(text="STALE", articles=[])
        self.unknowns.return_value = iter([])

        response = next(self.client.fresh_headlines([stale]), None)
        ham.assert_that(
            response,
            ham.none(),
            "If there are no fresh headlines, don't find any.",
        )

    def test_cleanup(self):
        now = datetime.datetime.now()
        self.config.age_limit = 3
        self.requests.get.return_value.json.return_value = episodes_with_dates(
            {
                1: now - datetime.timedelta(days=7),
                2: now - datetime.timedelta(days=2),
            }
        )
        self.client.cleanup(now)
        self.requests.get.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            params={"filter": "editable", "sorting": "oldest"},
        )

        self.requests.delete.assert_called_once_with(
            "THE_URL/v2/episodes/1",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
        )

    def test_truncate_title(self):
        limit = self.config.title_limit
        too_long = "a" * (limit + 1)
        truncated = "a" * (limit - len(spreaker.ELLIPSIS)) + spreaker.ELLIPSIS

        self.client.upload(title=too_long, audio=b"THE_AUDIO", description="")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry("data", ham.has_entry("title", truncated)),
        )

    @hyp.given(hyp.strategies.text())
    def test_truncate_title_property(self, title):
        self.client.upload(title=title, audio=b"THE_AUDIO", description="")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry(
                "data",
                ham.has_entry(
                    "title",
                    ham.has_length(ham.less_than_or_equal_to(self.config.title_limit)),
                ),
            ),
        )


# https://developers.spreaker.com/api/episodes/#retrieving-a-shows-episodes
def episodes_with_titles(titles):
    return {"response": {"items": [{"title": t} for t in titles]}}


def episodes_with_dates(id_date):
    return {
        "response": {
            "items": [
                {"episode_id": id, "published_at": date.strftime("%Y-%m-%d %H:%M:%S")}
                for id, date in id_date.items()
            ]
        }
    }
