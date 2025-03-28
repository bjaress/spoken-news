import unittest
from unittest import mock
import hamcrest as ham
import hypothesis as hyp
from hypothesis import strategies as st

from api import stories
from api import models


class TestSimple(unittest.TestCase):
    def setUp(self):
        self.tts_config = mock.Mock(length_limit=500, intro="INTRO", outro="OUTRO")

    def test_extraction(self):
        client = mock.MagicMock()
        reference = models.ArticleReference(title="Foo")
        headline = models.Headline(
            text="HEADLINE_TEXT",
            articles=[reference],
        )

        story = stories.extract_story(client, headline)

        client.fetch_and_parse_article.assert_called_with(reference)

        ham.assert_that(
            story,
            ham.has_properties(
                {
                    "articles": ham.contains_exactly(
                        client.fetch_and_parse_article.return_value
                    ),
                    "headline": "HEADLINE_TEXT",
                }
            ),
        )

    def test_text(self):
        article = mock_paragraphs("Summary text", "more")
        story = stories.Story("HEADLINE", [article])
        text = story.text(self.tts_config)
        assert text == "INTRO\n\nHEADLINE\n\nSummary text\n\nmore\n\nOUTRO", text

    def test_article_order(self):
        story = stories.Story(
            "HEADLINE",
            [
                mock_paragraphs("text", title="FooBarBaz"),
                mock_paragraphs("more", title="Foo"),
                # word count dominates length count
                mock_paragraphs("Summary", title="F B B"),
            ],
        )
        text = story.text(self.tts_config)
        assert text == "INTRO\n\nHEADLINE\n\nSummary\n\ntext\n\nmore\n\nOUTRO", text

    def test_sort_key_order(self):
        assert sort_key("a") < sort_key("b")
        assert sort_key("aa") > sort_key("b")
        assert sort_key("aa") < sort_key("ab")

        assert sort_key("a a") > sort_key("ab")
        assert sort_key("a a") < sort_key("a b")
        assert sort_key("a a") < sort_key("a b")

        assert sort_key("a_a") > sort_key("ab")
        assert sort_key("a_a") < sort_key("a_b")
        assert sort_key("a_a") < sort_key("a_b")

        assert sort_key("aaa") > sort_key("aa")
        assert sort_key("aaa") < sort_key("a a")

        assert sort_key("List of Hats") < sort_key("Hat")
        assert sort_key("List_of_Hats") < sort_key("Hat")


class TestTruncateStory(unittest.TestCase):
    def test_simple(self):
        story = stories.Story(
            "H",
            [
                mock_paragraphs(
                    "a",
                    "really long piece of text that will be skipped",
                    id=1,
                    title="first article in collection",
                ),
                mock_paragraphs("b", "c", id=2, title="second article"),
                mock_paragraphs(
                    "this entire article will be skipped", id=3, title="third"
                ),
            ],
        )
        text = story.text(mock.Mock(length_limit=30, intro="INTRO", outro="OUTRO"))
        assert text == "INTRO\n\nH\n\na\n\nb\n\nc\n\nOUTRO", text
        ham.assert_that(
            story.permalink_ids(),
            ham.has_entries(
                {
                    1: ham.has_properties({"title": "first article in collection"}),
                    2: ham.has_properties({"title": "second article"}),
                    3: ham.has_properties({"title": "third"}),
                }
            ),
        )

    def test_outro_budgeted(self):
        intro = "intro"
        headline = "HEADLINE"
        text_a = "a"
        text_b = "b"
        outro = "outro"
        story = stories.Story(headline, [mock_paragraphs(text_a, text_b)])
        a_only = f"{intro}\n\n{headline}\n\n{text_a}\n\n{outro}"
        both = f"{intro}\n\n{headline}\n\n{text_a}\n\n{text_b}\n\n{outro}"

        text = story.text(mock.Mock(length_limit=len(both), intro=intro, outro=outro))
        assert text == both, text

        # barely too short to contain text_b
        text = story.text(
            mock.Mock(length_limit=len(both) - 1, intro=intro, outro=outro)
        )
        assert text == a_only, text


def mock_paragraphs(*paragraphs, id=0, title="Title"):
    return mock.Mock(
        summary=paragraphs,
        permalink_id=id,
        reference=mock.Mock(title=title),
    )


def sort_key(title):
    article = mock.Mock()
    article.reference.title = title
    return stories.sort_key(article)


class TestByteBudgeting(unittest.TestCase):
    def test_no_existing(self):
        paragraphs, budget = stories.include_if_room([], 1, ["a"], len_sep=1)
        assert paragraphs == ["a"], paragraphs
        assert budget == 0, budget

    def test_no_additional(self):
        paragraphs, budget = stories.include_if_room([], 1, [], len_sep=1)
        assert paragraphs == [], paragraphs
        assert budget == 1, budget

    @hyp.given(st.lists(st.text()), st.integers(min_value=0), st.lists(st.text()))
    def test_consistency(self, paragraphs_before, budget_before, additional_paragraphs):
        inputs = (paragraphs_before, budget_before, additional_paragraphs)
        paragraphs_after, budget_after = stories.include_if_room(
            paragraphs_before, budget_before, additional_paragraphs
        )

        assert 0 <= budget_after <= budget_before, inputs

        len_before = len(stories.SEPARATOR.join(paragraphs_before).encode())
        len_after = len(stories.SEPARATOR.join(paragraphs_after).encode())
        assert len_after == len_before + (budget_before - budget_after), inputs
