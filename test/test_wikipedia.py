import unittest
from unittest import mock
import hamcrest as ham

import api.wikipedia as wikipedia


class TestClient(unittest.TestCase):
    def test_headlines_happypath(self):
        requests = mock.MagicMock()
        client = wikipedia.Client(
            {"url": "THE_URL", "headlines_page": "THE_HEADLINES"}, requests=requests
        )

        requests.get.assert_not_called()

        requests.get.return_value.json.return_value = {
            "parse": {
                "text": {
                    "*": """
                    <ul>
                        <li>Hello, <a href="/wiki/Earth">World</a>!</li>
                    </ul>
                    """
                }
            }
        }

        headlines = client.headlines()

        requests.get.assert_called_once_with(
            "THE_URL/w/api.php",
            params={
                "action": "parse",
                "section": 0,
                "prop": "text",
                "format": "json",
                "page": "THE_HEADLINES",
            },
        )

        ham.assert_that(
            headlines, ham.contains_exactly(ham.has_property("text", "Hello, World!"))
        )

    def test_headlines_multi(self):
        requests = mock.MagicMock()
        client = wikipedia.Client(
            {"url": "THE_URL", "headlines_page": "THE_HEADLINES"}, requests=requests
        )

        requests.get.return_value.json.return_value = {
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

        headlines = client.headlines()

        ham.assert_that(
            headlines,
            ham.contains_exactly(
                ham.has_property("text", "Goodby, World!"),
                ham.has_property("text", "Hello, World!"),
            ),
        )
