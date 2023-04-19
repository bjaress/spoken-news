import unittest
import hamcrest as ham
import hypothesis as hyp
from unittest import mock

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
        self.config = config
        self.requests = mock.Mock()
        self.client = spreaker.Client(config, requests=self.requests)

    def test_upload(self):
        self.requests.post.assert_not_called()
        self.client.upload(title="THE_TITLE", audio=b"THE_AUDIO")
        self.requests.post.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            # presence of files triggers the correct content-type
            files=[("media_file", ("audio.mp3", b"THE_AUDIO", "audio/mp3"))],
            data={"title": "THE_TITLE"},
        )

    def test_fresh_headline(self):
        fresh = models.Headline(text="THE_TITLE")
        self.requests.get.return_value.json.return_value = episodes_with_titles([])
        response = self.client.fresh_headline([fresh])

        self.requests.get.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            params={"filter": "editable"},
        )
        ham.assert_that(
            response, ham.equal_to(fresh), "The fresh headline should be chosen."
        )

    def test_fresh_headline_multiple(self):
        fresh_newer = models.Headline(text="NEWER")
        fresh_older = models.Headline(text="OLDER")
        self.requests.get.return_value.json.return_value = episodes_with_titles([])

        response = self.client.fresh_headline([fresh_newer, fresh_older])
        ham.assert_that(
            response,
            ham.equal_to(fresh_older),
            "The oldest fresh headline should be chosen.",
        )

    def test_fresh_headline_stale(self):
        fresh_newer = models.Headline(text="FRESH_NEWER")
        stale_older = models.Headline(text="STALE_OLDER")
        self.requests.get.return_value.json.return_value = episodes_with_titles(
            ["STALE_OLDER"]
        )

        response = self.client.fresh_headline([fresh_newer, stale_older])
        ham.assert_that(
            response,
            ham.equal_to(fresh_newer),
            "The oldest fresh headline should be chosen.",
        )

    def test_fresh_headline_stale_truncated(self):
        fresh_newer = models.Headline(text="FRESH_NEWER")
        stale_older = models.Headline(text=("long" * self.config.title_limit))
        assert len(stale_older.text) > self.config.title_limit
        self.requests.get.return_value.json.return_value = episodes_with_titles(
            [self.client.truncate_episode_title(stale_older.text)]
        )

        response = self.client.fresh_headline([fresh_newer, stale_older])
        ham.assert_that(
            response,
            ham.equal_to(fresh_newer),
            "The oldest fresh headline should be chosen.",
        )

    def test_fresh_headline_all_stale(self):
        stale = models.Headline(text="STALE")
        self.requests.get.return_value.json.return_value = episodes_with_titles(
            ["STALE"]
        )

        response = self.client.fresh_headline([stale])
        ham.assert_that(
            response,
            ham.none(),
            "If there are no fresh headlines, don't find any.",
        )

    def test_truncate_title(self):
        limit = self.config.title_limit
        too_long = "a" * (limit + 1)
        truncated = "a" * (limit - len(spreaker.ELLIPSIS)) + spreaker.ELLIPSIS

        self.client.upload(title=too_long, audio=b"THE_AUDIO")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry("data", ham.has_entry("title", truncated)),
        )

    @hyp.given(hyp.strategies.text())
    def test_truncate_title_property(self, title):
        self.client.upload(title=title, audio=b"THE_AUDIO")
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
