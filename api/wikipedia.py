import requests

API_PATH = "/w/api.php"


class Client:
    def __init__(self, options, requests=requests):
        self.requests = requests
        self.options = options
        self.endpoint = self.options["url"] + API_PATH

    def headlines(self):
        self.requests.get(
            self.endpoint,
            params={
                "action": "parse",
                "section": 0,
                "prop": "text",
                "format": "json",
                "page": self.options["headlines_page"],
            },
        )
