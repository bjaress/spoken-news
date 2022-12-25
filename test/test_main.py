import unittest
import hamcrest as h
from unittest.mock import Mock

from api import main


class TestMain(unittest.TestCase):
    @unittest.mock.patch("api.spreaker.Client")
    @unittest.mock.patch("api.tts.Client")
    def test_news(self, tts_Client, spreaker_Client):
        trigger = Mock()
        trigger.message.attributes.dict.return_value = {
            'tts_api_key': "THE_TTS_API_KEY",
            'spreaker_url': "THE_SPREAKER_URL",
            'spreaker_token': "THE_SPREAKER_TOKEN",
            'spreaker_show_id': "THE_SPREAKER_SHOW_ID",
        }

        response = main.generate_news(trigger)

        tts_Client.assert_called_with({'api_key': "THE_TTS_API_KEY"})
        tts_Client.return_value.speak.assert_called()

        spreaker_Client.assert_called_with({
            'url': "THE_SPREAKER_URL",
            'token': "THE_SPREAKER_TOKEN",
            'show_id': "THE_SPREAKER_SHOW_ID",
        })
        spreaker_Client.return_value.upload.assert_called()
