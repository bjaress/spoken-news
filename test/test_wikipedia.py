import unittest
from unittest import mock
import hamcrest as ham
import hypothesis as hyp
import hypothesis.strategies as st
import textwrap
import re

from bs4 import BeautifulSoup
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
                "revid": 1234,
                "text": {
                    "*": """
                    <div>
                    <ul>
                        <li><a href="/wiki/Greeting#Hello">Hello</a>,
                        <b><a href="/wiki/Earth">World</a></b>! (ignore this)</li>
                    </ul>
                    </div>
                    <div>
                        <b><a href="/wiki/Deaths_in_1492">Recent-ish deaths</a></b>:
                        <div>
                            <ul>
                                <li><a href="/wiki/Alice_Smith">Alice
                                Smith</a></li>
                            </ul>
                        </div>
                    </div>
                    """
                },
            }
        }

        headlines = self.client.headlines()

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.API_PATH}",
            params={
                "action": "parse",
                "section": 0,
                "redirects": "",
                "prop": "text|revid",
                "format": "json",
                "page": self.config.headlines_page,
            },
        )

        ham.assert_that(
            headlines,
            ham.contains_exactly(
                ham.has_properties(
                    {
                        "text": "Alice Smith dies.",
                        "articles": ham.contains_exactly(
                            ham.has_properties(
                                {
                                    "title": "Alice_Smith",
                                    "featured": False,
                                }
                            ),
                        ),
                    }
                ),
                ham.has_properties(
                    {
                        "text": "Hello, World!",
                        "articles": ham.contains_exactly(
                            ham.has_properties(
                                {
                                    "title": "Greeting",
                                    "section": "Hello",
                                    "featured": False,
                                }
                            ),
                            ham.has_properties(
                                {
                                    "title": "Earth",
                                    "featured": True,
                                }
                            ),
                        ),
                    }
                ),
            ),
        )

    def test_headlines_multi(self):

        self.requests.get.return_value.json.return_value = {
            "parse": {
                "revid": 1234,
                "text": {
                    "*": """
                    <ul>
                        <li>Hello, World!</li>
                        <li><a href="/wiki/%25#%26">percent, ampersand</a></li>
                    </ul>
                    """
                },
            }
        }

        headlines = self.client.headlines()

        ham.assert_that(
            headlines,
            ham.contains_exactly(
                ham.has_property("text", "Hello, World!"),
                ham.has_properties(
                    {
                        "text": "percent, ampersand",
                        "articles": ham.contains_exactly(
                            ham.has_properties(
                                {
                                    "title": "%",
                                    "section": "&",
                                }
                            )
                        ),
                    }
                ),
            ),
        )

    def test_describe_story(self):
        story = mock.Mock()
        story.permalink_ids.return_value = {
            123: mock.Mock(title="a"),
            456: mock.Mock(title="b"),
        }
        story.headline = "HEADLINE"
        expected = [
            "HEADLINE",
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


class TestHtmlHandling(unittest.TestCase):
    def setUp(self):
        self.requests = mock.MagicMock()
        self.config = mock.MagicMock()
        self.client = wikipedia.Client(self.config, requests=self.requests)

    def test_fetch_html(self):
        self.requests.get.return_value.json.return_value = {
            "parse": {"text": {"*": "<p>The text.</p>"}, "revid": 1234}
        }
        soup, version = article = self.client.fetch_html("The_Title")

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.API_PATH}",
            params={
                "action": "parse",
                "redirects": "",
                "section": 0,
                "prop": "text|revid",
                "format": "json",
                "page": "The_Title",
            },
        )

        ham.assert_that(soup.string, ham.contains_string("The text."))
        ham.assert_that(version, ham.equal_to(1234))

    def test_fetch_html_section(self):
        self.requests.get.return_value.json.return_value = {
            "parse": {"revid": 5678, "text": {"*": "<p>The text.</p>"}}
        }
        soup, version = self.client.fetch_html("The_Other_Title", 7)

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.API_PATH}",
            params={
                "action": "parse",
                "redirects": "",
                "section": 7,
                "prop": "text|revid",
                "format": "json",
                "page": "The_Other_Title",
            },
        )

        ham.assert_that(soup.string, ham.contains_string("The text."))
        ham.assert_that(version, ham.equal_to(5678))

    def test_section_index_for_reference(self):
        self.requests.get.return_value.json.return_value = {
            "parse": {
                "sections": [
                    {
                        "index": 123,
                        "linkAnchor": "Weird_section",
                    },
                    {
                        "index": 456,
                        "linkAnchor": "Cool_section",
                    },
                    {
                        "index": 789,
                        "linkAnchor": "Boring_section",
                    },
                ]
            }
        }
        id = self.client.section_index_for_reference(
            models.ArticleReference(
                title="The_Title", section="Cool_section", featured=False
            )
        )

        self.requests.get.assert_called_once_with(
            f"{self.config.url}{wikipedia.API_PATH}",
            params={
                "action": "parse",
                "prop": "sections",
                "format": "json",
                "page": "The_Title",
            },
        )

        ham.assert_that(id, ham.equal_to(456))

    def test_section_index_for_reference_default(self):
        id = self.client.section_index_for_reference(
            models.ArticleReference(title="The_Title", featured=False)
        )
        ham.assert_that(id, ham.equal_to(0))

    def test_fetch_and_parse_article(self):
        self.client.fetch_html = mock.MagicMock()
        self.client.section_index_for_reference = mock.MagicMock()
        self.client.extract_text_chunks = mock.MagicMock()

        reference = models.ArticleReference(
            title="The_Title", section="Cool_section", featured=False
        )
        self.client.fetch_html.return_value = ("soup", 1234)
        self.client.extract_text_chunks.return_value = ["some text"]
        article = self.client.fetch_and_parse_article(reference)

        self.client.section_index_for_reference.assert_called_with(reference)
        self.client.fetch_html.assert_called_with(
            "The_Title", self.client.section_index_for_reference.return_value
        )
        self.client.extract_text_chunks.assert_called_with("soup")

        ham.assert_that(
            article,
            ham.has_properties(
                {
                    "summary": self.client.extract_text_chunks.return_value,
                    "permalink_id": 1234,
                    "reference": reference,
                }
            ),
        )

    def test_extract_text_chunks(self):
        html = """
        <h3>Omit This</h3>

        <ul><li>omit this</li></ul>
        <p>omit this</p>
        <p>One two <a
            href="ignore url" title="ignore title">three</a>.<sup><a
            href="#cite_note-2">[2]</a><a
            href="#cite_note-3">[3]</a></sup>
            <em>Four</em> <strong>five</strong>.
            <a href="/wiki/Wikipedia:Disputed_statement">[omit this]</a>
            <a href="/wiki/Help:Cite_errors">[omit this]</a>
        </p>
        <p>Cite error: omit this</p>
        <ul>
            <li>six</li>
            <li>seven</li>
        </ul>
        <p>Eight (omit this).</p>
        <ol>
            <li><strong><a href="#cite_ref-1">^</a></strong> Omit this.</li>
        </ol>
        """
        expect = ["One two three. Four five.", "  - six\n  - seven", "Eight."]
        soup = BeautifulSoup(html)
        result = self.client.extract_text_chunks(soup)

        ham.assert_that(result, ham.contains_exactly(*expect), result)


# Inspired by clever folks on the Internet.
#
# Uses an iterator to always scan only forward in seq_b looking for the
# very next item in seq_a.  Each new item from seq_a consumes as much as
# it has to from the iterator of seq_b, so the next item starts
# consuming from that point in the iterator.
def is_subseq(seq_a, seq_b):
    forward_only = iter(seq_b)
    return all(item in forward_only for item in seq_a)
