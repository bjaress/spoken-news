import unittest
from unittest import mock
import hamcrest as ham
import hypothesis as hyp
import hypothesis.strategies as st
import textwrap
import re

import api.wikipedia as wikipedia
import api.models as models


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
                        <li><a href="/wiki/Greeting#Hello">Hello</a>,
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
                        "articles": ham.contains_exactly(
                            ham.has_properties(
                                {
                                    "title": "Greeting",
                                    "section": "Hello",
                                }
                            ),
                            ham.has_properties({"title": "Earth"}),
                        ),
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
                (ignore) <ref>ignore</ref> <ref name="bs"/>
                [[File:ignore.jpg|ignore]]
                """,
        }
        reference = models.ArticleReference(title="The_Title")
        article = self.client.fetch_article(reference)

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.PAGE_PATH}/The_Title"
        )

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": "Hello, bold link.",
                    "permalink_id": 123,
                    "reference": reference,
                }
            ),
        )

    def test_fetch_article_with_section(self):
        self.requests.get.return_value.json.return_value = {
            "latest": {"id": 123},
            "source": textwrap.dedent(
                """
                Ignored.

                ==Some Other Section==

                Ignored.

                ==The Section==

                Hello, Section!
                """
            ),
        }
        reference = models.ArticleReference(title="The_Title", section="The_Section")
        article = self.client.fetch_article(reference)

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.PAGE_PATH}/The_Title"
        )

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": "Hello, Section!",
                    "permalink_id": 123,
                    "reference": reference,
                }
            ),
        )

    def test_describe_story(self):
        story = mock.Mock()
        story.permalink_ids.return_value = {
            123: mock.Mock(title="a"),
            456: mock.Mock(title="b"),
        }
        expected = [
            "https://creativecommons.org/licenses/by-sa/4.0/",
            "oldid=123",
            "oldid=456",
            "title=a",
            "title=b",
        ]

        ham.assert_that(
            self.client.describe(story),
            ham.all_of(*[ham.contains_string(s) for s in expected]),
        )


class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.requests = mock.MagicMock()
        self.config = mock.MagicMock()
        self.client = wikipedia.Client(self.config, requests=self.requests)

    def test_convert_units(self):
        self.requests.get.return_value.json.return_value = {
            "latest": {"id": 123},
            "source": """
                {{convert|220|km|sp=us}} and {{convert|1|to|3|ft|m|sp=us}}
                """,
        }
        reference = models.ArticleReference(title="The_Title")
        article = self.client.fetch_article(reference)

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": "220 km and 1 to 3 ft",
                }
            ),
        )

    def test_convert_units_decimal(self):
        self.requests.get.return_value.json.return_value = {
            "latest": {"id": 123},
            "source": """
                {{convert|22.0|km|sp=us}} and {{convert|1.2|to|3.4|ft|m|sp=us}}
                """,
        }
        reference = models.ArticleReference(title="The_Title")
        article = self.client.fetch_article(reference)

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": "22.0 km and 1.2 to 3.4 ft",
                }
            ),
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


class TestHelperEdges(unittest.TestCase):
    def test_section_text_link_error(self):
        section = mock.MagicMock()
        section.get_tags.return_value = []
        section.contents = "Hello"

        link = mock.MagicMock()
        section.wikilinks = [link]
        link.target.startswith.side_effect = AttributeError()
        result = wikipedia.section_text(None, [section])
        assert result == "Hello", result

    def test_permalink_parens(self):
        result = wikipedia.permalink("BASE", "Title (paren)", "ID")
        ham.assert_that(
            result,
            ham.all_of(
                ham.starts_with("BASE"),
                ham.contains_string("title=Title%20%28paren%29"),
                ham.contains_string("oldid=ID"),
            ),
        )

    @hyp.given(st.text(), st.text())
    def test_permalink_property(self, title, id):
        base = "BASE"
        result = wikipedia.permalink(base, title, id)
        assert result.startswith(base), result
        match = re.fullmatch(base + r"\?[a-zA-Z0-9=&%/~._-]+", result)
        assert match is not None, result


# Inspired by clever folks on the Internet.
#
# Uses an iterator to always scan only forward in seq_b looking for the
# very next item in seq_a.  Each new item from seq_a consumes as much as
# it has to from the iterator of seq_b, so the next item starts
# consuming from that point in the iterator.
def is_subseq(seq_a, seq_b):
    forward_only = iter(seq_b)
    return all(item in forward_only for item in seq_a)
