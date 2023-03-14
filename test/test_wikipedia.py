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

        client.headlines()

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
