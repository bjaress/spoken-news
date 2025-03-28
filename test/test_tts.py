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

        story = mock.MagicMock()
        story.text.return_value = "THE_WORDS"
        result = client.speak(story)
        story.text.assert_called_with(config)
        h.assert_that(
            requests.post.call_args.kwargs,
            h.has_entries(
                {
                    "url": "THE_SERVER/v1/text:synthesize?key=THE_API_KEY",
                    "json": h.has_entries(
                        {
                            "input": {"text": "THE_WORDS"},
                            "voice": h.has_entries(
                                {
                                    "languageCode": h.anything(),
                                    "name": h.anything(),
                                }
                            ),
                            "audioConfig": h.has_entries(
                                {
                                    "audioEncoding": "MP3",
                                }
                            ),
                        }
                    ),
                }
            ),
        )
        h.assert_that(result, h.equal_to(base64.b64decode("000MP3BASE64")))
