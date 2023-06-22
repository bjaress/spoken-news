import unittest
from unittest import mock
import hamcrest as ham

from api import editing
from api import models


class TestSimple(unittest.TestCase):
    def test_extraction(self):
        client = mock.MagicMock()
        client.summary.return_value = "Summary text\n\nmore"
        headline = models.Headline(
            text="",
            articles=["Foo"],
        )

        plan = editing.extract_plan(client, headline)

        client.summary.assert_called_with("Foo")

        ham.assert_that(
            plan.summaries, ham.has_entries({"Foo": ["Summary text", "more"]})
        )

    def test_text(self):
        plan = editing.Plan({"Foo": ["Summary text", "more"]})
        text = plan.text(500)
        assert text == "Summary text\n\nmore", text

    def test_article_order(self):
        plan = editing.Plan(
            {
                "FooBarBaz": ["text"],
                "Foo": ["more"],
                # word count dominates length count
                "F B B": ["Summary"],
            }
        )
        text = plan.text(500)
        assert text == "Summary\n\ntext\n\nmore", text


class TestTruncate(unittest.TestCase):
    def test_simple(self):
        plan = editing.Plan(
            {
                "first article in collection": [
                    "a",
                    "really long piece of text that will be skipped",
                ],
                "second article": ["b", "c"],
                "third": ["this entire article will be skipped"],
            }
        )
        text = plan.text(10)
        assert text == "a\n\nb\n\nc", text

    def test_no_existing(self):
        paragraphs, budget = editing.include_if_room([], 1, ["a"], len_sep=1)
        assert paragraphs == ["a"], paragraphs
        assert budget == 0, budget

    def test_no_additional(self):
        paragraphs, budget = editing.include_if_room([], 1, [], len_sep=1)
        assert paragraphs == [], paragraphs
        assert budget == 1, budget

    # TODO property test
