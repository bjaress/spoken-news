import unittest
import hamcrest as h
from unittest import mock

import base64

from api import tts


class TestVoiceSelection(unittest.TestCase):

    def test_pick_voice(self):
        languages = {"xx-XX": 1, "yy-YY": 2}
        personalities = ["Alice", "Bob"]

        random = mock.MagicMock()
        random.choices.return_value = ["THE_CHOSEN_LANGUAGE"]
        random.choice.return_value = "THE_CHOSEN_PERSONALITY"

        voice = tts.pick_voice(
            languages=languages, personalities=personalities, random=random
        )

        h.assert_that(
            voice,
            h.has_properties(
                {
                    "name": "THE_CHOSEN_LANGUAGE-Chirp3-HD-THE_CHOSEN_PERSONALITY",
                    "language": "THE_CHOSEN_LANGUAGE",
                }
            ),
        )

        random.choice.assert_called_once_with(personalities)
        random.choices.assert_called_once_with(["xx-XX", "yy-YY"], [1, 2], k=1)


class TestTtsClient(unittest.TestCase):
    def test_speak(self):
        config = mock.MagicMock()
        config.api_key = "THE_API_KEY"
        config.server = "THE_SERVER"

        pick_voice = mock.MagicMock()
        pick_voice.return_value = tts.VoiceProfile("THE_VOICE_NAME", "THE_LANGUAGE")

        requests = mock.Mock()
        client = tts.Client(config, requests=requests, pick_voice=pick_voice)

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
                                    "languageCode": "THE_LANGUAGE",
                                    "name": "THE_VOICE_NAME",
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
