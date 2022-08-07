
import unittest
import hamcrest as ham
import app.storage_client as storage_client

class TestStorage(unittest.TestCase):

    def test_create(self):
        storage_endpoint = "the-endpoint.com"
        module = unittest.mock.MagicMock()
        storage = storage_client.Storage(
            storage_endpoint,
            module=module)

        module.Client.assert_called_with({ 'api_endpoint': storage_endpoint})
        ham.assert_that(
            storage.client,
            ham.equal_to(module.Client.return_value))

    def test_fetch_oauth_refresh_token(self):
        storage = storage_client.Storage(
            "the-endpoint.com",
            unittest.mock.MagicMock())

        token = storage.fetch_oauth_refresh_token()
