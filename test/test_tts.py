import unittest
import hamcrest as h
from unittest.mock import Mock

from api import tts


class TestTtsClient(unittest.TestCase):
    def test_speak(self):
        config = {"api_key": "THE_API_KEY", "server": "THE_SERVER"}
        requests = Mock()
        client = tts.Client(config, requests=requests)
        requests.post.assert_not_called()

        client.speak("THE_WORDS")
        requests.post.assert_called_with(
            url="THE_SERVER/v1/text:synthesize?key=THE_API_KEY",
            json={
                "input": {"text": "THE_WORDS"},
                "voice": {
                    "languageCode": "en-gb",
                    "name": "en-GB-Standard-A",
                    "ssmlGender": "FEMALE",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            },
        )
