import unittest
import hamcrest as h
from unittest.mock import Mock

from api import main


class TestMain(unittest.TestCase):
    @unittest.mock.patch("api.spreaker.Client")
    def test_news(self, spreaker_Client):
        trigger = Mock()
        spreaker = Mock()
        response = main.generate_news(trigger)

        spreaker_Client.assert_called_with(trigger.spreaker)
        spreaker_Client.return_value.upload.assert_called_with(
            title="Dummy Title", audio=b"dummy"
        )
