import unittest
import hamcrest as h
from unittest import mock

import base64

from api import tts


class TestTtsClient(unittest.TestCase):
    def test_speak(self):
        config = mock.MagicMock()
        config.api_key = "THE_API_KEY"
        config.server = "THE_SERVER"

        requests = mock.Mock()
        client = tts.Client(config, requests=requests)

        requests.post.assert_not_called()
        requests.post.return_value.json.return_value = {"audioContent": "000MP3BASE64"}

        result = client.speak("THE_WORDS")
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
        h.assert_that(result, h.equal_to(base64.b64decode("000MP3BASE64")))
