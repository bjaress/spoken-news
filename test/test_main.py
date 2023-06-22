import unittest
import hamcrest as h
from unittest.mock import Mock, MagicMock
import datetime as dt

from api import models
from api import main


class TestNews(unittest.TestCase):
    def test_news(self):
        clients = Mock()
        editing = Mock()
        main.generate_news(clients, editing=editing)

        clients.spreaker.fresh_headline.assert_called_with(
            clients.wikipedia.headlines.return_value
        )

        headline = clients.spreaker.fresh_headline.return_value

        editing.extract_plan.assert_called_with(clients.wikipedia, headline)
        clients.tts.speak.assert_called_with(editing.extract_plan.return_value)
        clients.spreaker.upload.assert_called_with(
            title=headline.text, audio=clients.tts.speak.return_value
        )

    def test_news_no_fresh(self):
        clients = Mock()
        editing = Mock()
        clients.spreaker.fresh_headline.return_value = None
        main.generate_news(clients, editing)

        clients.tts.speak.assert_not_called()
        clients.spreaker.upload.assert_not_called()


class TestCleanup(unittest.TestCase):
    def test_cleanup(self):
        spreaker = Mock()
        main.cleanup(spreaker)
        spreaker.cleanup.assert_called()
        (cutoff,) = spreaker.cleanup.call_args.args
        assert isinstance(cutoff, dt.datetime)


DUMMY_ATTRIBUTES = {
    "tts_api_key": "THE_TTS_API_KEY",
    "tts_server": "THE_TTS_SERVER",
    "tts_length_limit": 50,
    "spreaker_url": "THE_SPREAKER_URL",
    "spreaker_token": "THE_SPREAKER_TOKEN",
    "spreaker_show_id": 1234,
    "spreaker_title_limit": 1234,
    "spreaker_age_limit": 30,
    "wikipedia_url": "THE_WIKIPEDIA_URL",
    "wikipedia_headlines_page": "THE_WIKIPEDIA_HEADLINES",
}


class TestClientConfigs(unittest.TestCase):
    def test_decompose_attributes(self):
        attributes = models.Attributes(**DUMMY_ATTRIBUTES)
        result = main.decompose_attributes(
            models.NewsTrigger(message=models.NewsMessage(attributes=attributes))
        )

        h.assert_that(
            result,
            h.has_properties(
                {
                    "spreaker": h.has_properties(
                        {
                            "url": attributes.spreaker_url,
                            "token": attributes.spreaker_token,
                            "show_id": attributes.spreaker_show_id,
                            "age_limit": 30,
                        }
                    ),
                    "wikipedia": h.has_properties(
                        {
                            "url": attributes.wikipedia_url,
                            "headlines_page": attributes.wikipedia_headlines_page,
                        }
                    ),
                    "tts": h.has_properties(
                        {
                            "server": attributes.tts_server,
                            "api_key": attributes.tts_api_key,
                        }
                    ),
                }
            ),
        )


class TestClients(unittest.TestCase):
    @unittest.mock.patch("api.wikipedia.Client")
    @unittest.mock.patch("api.spreaker.Client")
    @unittest.mock.patch("api.tts.Client")
    def test_init(self, tts_Client, spreaker_Client, wikipedia_Client):
        config = Mock()
        result = main.Clients(config)
        h.assert_that(
            result,
            h.has_properties(
                {
                    "tts": tts_Client.return_value,
                    "spreaker": spreaker_Client.return_value,
                    "wikipedia": wikipedia_Client.return_value,
                }
            ),
        )

        tts_Client.assert_called_with(config.tts)
        spreaker_Client.assert_called_with(config.spreaker)
        wikipedia_Client.assert_called_with(config.wikipedia)
