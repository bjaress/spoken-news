import unittest
from unittest import mock
import hamcrest as ham
import hypothesis as hyp
import hypothesis.strategies as st

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
                        <a href="/wiki/Earth">World</a>! (ignore this)</li>
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

    def test_fetch_article(self):
        self.requests.get.return_value.json.return_value = {
            "latest": {"id": 123},
            "source": """
                Hello, '''bold''' [[link]].
                (ignore) <ref>ignore</ref> <ref name="bs">ignore</ref>
                """,
        }
        article = self.client.fetch_article("The_Title")

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.PAGE_PATH}/The_Title"
        )

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": "Hello, bold link.",
                    "permalink_id": 123,
                }
            ),
        )

    def test_simple(self):
        story = mock.Mock()
        story.permalink_ids.return_value = {"a": 1, "b": 2}
        expected = [
            "https://creativecommons.org/licenses/by-sa/4.0/",
            "oldid=1",
            "oldid=2",
            "title=a",
            "title=b",
        ]

        ham.assert_that(
            self.client.describe(story),
            ham.all_of(*[ham.contains_string(s) for s in expected]),
        )


class TestParentheses(unittest.TestCase):
    def test_with_comma(self):
        result = wikipedia.remove_parenthesized("a (b), c")
        assert result == "a, c", result

    def test_nested(self):
        result = wikipedia.remove_parenthesized("a (b (c) d) e")
        assert result == "a e", result

    def test_linebreak(self):
        result = wikipedia.remove_parenthesized("a (b (c) \nd) e")
        assert result == "a e", result

    def test_paragraph(self):
        # This would only come from badly-edited text on Wikipedia.
        result = wikipedia.remove_parenthesized("a (b (c) \n\nd e")
        assert result == "a\n\nd e", result

    @hyp.given(st.text())
    def test_subsequence(self, input):
        result = wikipedia.remove_parenthesized(input)
        assert is_subseq(result, input), (result, input)


# Inspired by clever folks on the Internet.
#
# Uses an iterator to always scan only forward in seq_b looking for the
# very next item in seq_a.  Each new item from seq_a consumes as much as
# it has to from the iterator of seq_b, so the next item starts
# consuming from that point in the iterator.
def is_subseq(seq_a, seq_b):
    forward_only = iter(seq_b)
    return all(item in forward_only for item in seq_a)
