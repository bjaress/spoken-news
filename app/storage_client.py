import google.cloud.storage.client as google_client

class Storage:
    def __init__(self, api_endpoint, module=google_client):
        self.client = module.Client({'api_endpoint': api_endpoint})
