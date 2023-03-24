import unittest
import hamcrest as h
from unittest.mock import Mock

from api import main


class TestMain(unittest.TestCase):
    @unittest.mock.patch("api.wikipedia.Client")
    @unittest.mock.patch("api.spreaker.Client")
    @unittest.mock.patch("api.tts.Client")
    def test_news(self, tts_Client, spreaker_Client, wikipedia_Client):
        trigger = Mock()
        trigger.message.attributes.dict.return_value = {
            "tts_api_key": "THE_TTS_API_KEY",
            "tts_server": "THE_TTS_SERVER",
            "spreaker_url": "THE_SPREAKER_URL",
            "spreaker_token": "THE_SPREAKER_TOKEN",
            "spreaker_show_id": "THE_SPREAKER_SHOW_ID",
            "wikipedia_url": "THE_WIKIPEDIA_URL",
            "wikipedia_headlines_page": "THE_WIKIPEDIA_HEADLINES",
        }

        headline = wikipedia_Client.return_value.headlines.return_value[0]
        headline.text = "Hello, Wikipedia!"
        tts_Client.return_value.speak.return_value = b"THE_MP3_DATA"
        response = main.generate_news(trigger)

        wikipedia_Client.assert_called_with(
            {"url": "THE_WIKIPEDIA_URL", "headlines_page": "THE_WIKIPEDIA_HEADLINES"}
        )
        wikipedia_Client.return_value.headlines.assert_called_once()

        # Use past episode list to pick a fresh headline
        spreaker_Client.return_value.fresh_headline.assert_called_with(
            wikipedia_Client.return_value.headlines.return_value
        )

        tts_Client.assert_called_with(
            {"api_key": "THE_TTS_API_KEY", "server": "THE_TTS_SERVER"}
        )
        tts_Client.return_value.speak.assert_called_with(headline.text)

        spreaker_Client.assert_called_with(
            {
                "url": "THE_SPREAKER_URL",
                "token": "THE_SPREAKER_TOKEN",
                "show_id": "THE_SPREAKER_SHOW_ID",
            }
        )
        spreaker_Client.return_value.upload.assert_called_with(
            title=headline.text,
            audio=b"THE_MP3_DATA",
        )
