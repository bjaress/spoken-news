import unittest
from unittest import mock
import hamcrest as ham

import api.wikipedia as wikipedia


class TestClient(unittest.TestCase):
    def setUp(self):
        self.requests = mock.MagicMock()
        self.config = mock.MagicMock()
        self.client = wikipedia.Client(self.config, requests=self.requests)

    def test_headlines_happypath(self):

        self.requests.get.assert_not_called()

        self.requests.get.return_value.json.return_value = {
            "parse": {
                "text": {
                    "*": """
                    <ul>
                        <li><a href="/wiki/Greeting">Hello</a>,
                        <a href="/wiki/Earth">World</a>!</li>
                    </ul>
                    """
                }
            }
        }

        headlines = self.client.headlines()

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.API_PATH}",
            params={
                "action": "parse",
                "section": 0,
                "prop": "text",
                "format": "json",
                "page": self.config.headlines_page,
            },
        )

        ham.assert_that(
            headlines,
            ham.contains_exactly(
                ham.has_properties(
                    {
                        "text": "Hello, World!",
                        "articles": ham.contains_exactly("Greeting", "Earth"),
                    }
                )
            ),
        )

    def test_headlines_multi(self):

        self.requests.get.return_value.json.return_value = {
            "parse": {
                "text": {
                    "*": """
                    <ul>
                        <li>Goodby, World!</li>
                        <li>Hello, World!</li>
                    </ul>
                    """
                }
            }
        }

        headlines = self.client.headlines()

        ham.assert_that(
            headlines,
            ham.contains_exactly(
                ham.has_property("text", "Goodby, World!"),
                ham.has_property("text", "Hello, World!"),
            ),
        )

    def test_summary(self):
        self.requests.get.return_value.json.return_value = {
            "source": "Hello, '''bold''' [[link]]."
        }
        summary = self.client.summary("The_Title")

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.PAGE_PATH}/The_Title"
        )

        assert summary == "Hello, bold link.", f"summary is {summary}"
