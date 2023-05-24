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
        text = plan.text()
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
        text = plan.text()
        assert text == "Summary\n\ntext\n\nmore", text
