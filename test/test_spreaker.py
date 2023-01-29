import unittest
import hamcrest as h
from unittest.mock import Mock

from api import spreaker

from requests.exceptions import HTTPError


class TestSpreaker(unittest.TestCase):
    def test_upload(self):
        config = {
            "url": "THE_URL",
            "token": "THE_TOKEN",
            "show_id": 0,
        }
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


#    def test_failed_upload(self):
#        config = {
#            "url": "THE_URL",
#            "token": "THE_TOKEN",
#            "show_id": 0,
#        }
#        requests = Mock()
#        client = spreaker.Client(config, requests=requests)
#        requests.post.return_value.raise_for_status.side_effect=HTTPError()
#        with self.assertRaises(HTTPError):
#            client.upload(title="THE_TITLE", audio=b"THE_AUDIO")
