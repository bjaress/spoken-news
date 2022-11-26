import unittest
import hamcrest as h
from unittest.mock import Mock

from api import spreaker
from api import models


class TestSpreaker(unittest.TestCase):
    def test_upload(self):
        config = models.Attributes(
            spreaker_url="THE_URL", spreaker_token="THE_TOKEN", spreaker_show_id=0
        )
        requests = Mock()
        client = spreaker.Client(config, requests=requests)

        requests.post.assert_not_called()
        client.upload(title="THE_TITLE", audio=b"THE_AUDIO")
        requests.post.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
            },
            # presence of files triggers the correct content-type
            files=[("media_file", ("audio.mp3", b"THE_AUDIO", "audio/mp3"))],
            data={"title": "THE_TITLE"},
        )
