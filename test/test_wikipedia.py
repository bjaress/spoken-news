import unittest
from unittest import mock
import hamcrest as ham

import api.wikipedia as wikipedia

class TestClient(unittest.TestCase):
    def test_headlines_happypath(self):
        external=mock.MagicMock()
        client = wikipedia.Client(wikipediaapi=external)

        external.Wikipedia.assert_called_once_with(
            language='en',
            extract_format=external.ExtractFormat.HTML)

        page_fetch = external.Wikipedia.return_value.page
        page_fetch.return_value.summary = """
            <ul>
                <li>
                    Some <a href="thingy/or/event">news</a> happened.
                </li>
            </ul>
            """
        headlines = client.headlines()
        page_fetch.assert_called_once_with(wikipedia.HEADLINE_PAGE)

        ham.assert_that(headlines,
            ham.contains_exactly(
                ham.all_of(
                    ham.has_property("text", "Some news happened."))))
