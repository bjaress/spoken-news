import requests


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.config = config

    def speak(self, words):
        self.requests.post(
            url=(
                self.config["server"]
                + "/v1/text:synthesize?key="
                + self.config["api_key"]
            )
        )
