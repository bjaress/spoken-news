import unittest
import hamcrest as ham
import hypothesis as hyp
from unittest.mock import Mock

import api.models as models
from api import spreaker

from requests.exceptions import HTTPError


class TestSpreaker(unittest.TestCase):
    def setUp(self):
        config = {
            "url": "THE_URL",
            "token": "THE_TOKEN",
            "show_id": 0,
        }
        self.requests = Mock()
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
        self.requests.get.assert_not_called()
        self.client.fresh_headline([models.Headline(text="THE_TITLE")])
        self.requests.get.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            params={"filter": "editable"},
        )

    def test_truncate_title(self):
        self.client.upload(title=("a" * 141), audio=b"THE_AUDIO")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry("data", ham.has_entry("title", "a" * 137 + "...")),
        )

    @hyp.given(hyp.strategies.text(max_size=spreaker.TITLE_LIMIT))
    def test_truncate_title_short(self, title):
        self.client.upload(title=title, audio=b"THE_AUDIO")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry("data", ham.has_entry("title", title)),
        )

    @hyp.given(hyp.strategies.text(min_size=2))
    def test_truncate_title_short(self, title):
        # It's slow to produce very long text in Hypothesis
        title = ("a" * (spreaker.TITLE_LIMIT - 1)) + title
        self.client.upload(title=title, audio=b"THE_AUDIO")
        ham.assert_that(
            self.requests.post.call_args.kwargs,
            ham.has_entry(
                "data",
                ham.has_entry(
                    "title",
                    ham.all_of(
                        ham.has_length(spreaker.TITLE_LIMIT),
                        ham.ends_with(spreaker.ELLIPSIS),
                    ),
                ),
            ),
        )
