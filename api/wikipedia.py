import requests
import re
from api import models
from bs4 import BeautifulSoup
import wikitextparser as wtp

import logging

API_PATH = "/w/api.php"
PAGE_PATH = "/w/rest.php/v1/page"


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

        headlines = [extract_headline(item) for item in soup.ul.find_all("li")]
        return headlines

    def summary(self, title):
        response = self.requests.get(f"{self.config.url}{PAGE_PATH}/{title}")
        markup = response.json()["source"]
        parsed = wtp.parse(markup)
        intro = parsed.get_sections()[0]
        return intro.plain_text().strip()


def extract_headline(li_element):
    return models.Headline(
        text=collapse(li_element.text),
        articles=[path_final(link["href"]) for link in li_element.select("a[href]")],
    )


def path_final(url):
    return url.split("/")[-1]


def collapse(string):
    return re.sub(r"\s+", " ", string)
