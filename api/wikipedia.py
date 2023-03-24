import requests
from api import models
from bs4 import BeautifulSoup

import logging

API_PATH = "/w/api.php"


class Client:
    def __init__(self, options, requests=requests):
        self.requests = requests
        self.options = options
        self.endpoint = self.options["url"] + API_PATH

    def headlines(self):
        response = self.requests.get(
            self.endpoint,
            params={
                "action": "parse",
                "section": 0,
                "prop": "text",
                "format": "json",
                "page": self.options["headlines_page"],
            },
        )
        logging.info(f"Wikipedia Request: {response.status_code}")

        html = response.json()["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")

        headlines = [models.Headline(text=item.text) for item in soup.ul.find_all("li")]
        return headlines
