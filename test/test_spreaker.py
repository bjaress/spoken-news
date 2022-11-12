import unittest
import hamcrest as h
from unittest.mock import Mock

from api import spreaker


class TestSpreaker(unittest.TestCase):
    def test_upload(self):
        config = spreaker.Config(url="THE_URL", token="THE_TOKEN", show_id=0)
        requests = Mock()
        client = spreaker.Client(config, requests=requests)

        requests.post.assert_not_called()
        client.upload()
        requests.post.assert_called_with(
            "THE_URL/v2/shows/0/episodes",
            headers={
                "Authorization": "Bearer THE_TOKEN",
                })
