import requests
from api import models
from bs4 import BeautifulSoup

import logging

API_PATH = "/w/api.php"


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.config = config

    def headlines(self):
        response = self.requests.get(
            f"{self.config.url}{API_PATH}",
            params={
                "action": "parse",
                "section": 0,
                "prop": "text",
                "format": "json",
                "page": self.config.headlines_page,
            },
        )
        logging.info(f"Wikipedia Request: {response.status_code}")

        html = response.json()["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")

        headlines = [models.Headline(text=item.text) for item in soup.ul.find_all("li")]
        return headlines
