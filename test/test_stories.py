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
        client.summary.return_value = "Summary text\n\nmore"
        headline = models.Headline(
            text="",
            articles=["Foo"],
        )

        story = stories.extract_story(client, headline)

        client.summary.assert_called_with("Foo")

        ham.assert_that(
            story.summaries, ham.has_entries({"Foo": ["Summary text", "more"]})
        )

    def test_text(self):
        story = stories.Story({"Foo": ["Summary text", "more"]})
        text = story.text(self.tts_config)
        assert text == "INTRO\n\nSummary text\n\nmore\n\nOUTRO", text

    def test_article_order(self):
        story = stories.Story(
            {
                "FooBarBaz": ["text"],
                "Foo": ["more"],
                # word count dominates length count
                "F B B": ["Summary"],
            }
        )
        text = story.text(self.tts_config)
        assert text == "INTRO\n\nSummary\n\ntext\n\nmore\n\nOUTRO", text


class TestTruncateStory(unittest.TestCase):
    def test_simple(self):
        story = stories.Story(
            {
                "first article in collection": [
                    "a",
                    "really long piece of text that will be skipped",
                ],
                "second article": ["b", "c"],
                "third": ["this entire article will be skipped"],
            }
        )
        text = story.text(mock.Mock(length_limit=30, intro="INTRO", outro="OUTRO"))
        assert text == "INTRO\n\na\n\nb\n\nc\n\nOUTRO", text

    def test_outro_budgeted(self):
        intro = "intro"
        text_a = "a"
        text_b = "b"
        outro = "outro"
        a_only = f"{intro}\n\n{text_a}\n\n{outro}"
        both = f"{intro}\n\n{text_a}\n\n{text_b}\n\n{outro}"
        story = stories.Story({"": [text_a, text_b]})

        text = story.text(mock.Mock(length_limit=len(both), intro=intro, outro=outro))
        assert text == both, text

        # barely too short to contain text_b
        text = story.text(
            mock.Mock(length_limit=len(both) - 1, intro=intro, outro=outro)
        )
        assert text == a_only, text


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
