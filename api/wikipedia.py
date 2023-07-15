import requests
import re
from api import models
from bs4 import BeautifulSoup
import wikitextparser as wtp

import logging

API_PATH = "/w/api.php"
PAGE_PATH = "/w/rest.php/v1/page"

LICENSE_NOTICE = """
Created from parts of Wikipedia articles and available under the CC
BY-SA 4.0 license: https://creativecommons.org/licenses/by-sa/4.0/
"""


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

    def fetch_article(self, title):
        response = self.requests.get(f"{self.config.url}{PAGE_PATH}/{title}")
        json = response.json()
        parsed = wtp.parse(json["source"])
        intro = parsed.get_sections()[0]
        for ref in parsed.get_tags("ref"):
            ref.contents = ""
        return models.Article(
            summary=remove_parenthesized(intro.plain_text()).strip(),
            permalink_id=json["latest"]["id"],
        )

    def describe(self, story):
        notice = " ".join(LICENSE_NOTICE.split())
        parts = notice, *(
            permalink(title, id) for title, id in story.permalink_ids().items()
        )
        return "\n".join(parts)


def permalink(title, id):
    return f"https://en.wikipedia.org/w/index.php?title={title}&oldid={id}"


def extract_headline(li_element):
    return models.Headline(
        text=remove_parenthesized(collapse(li_element.text)),
        articles=[path_final(link["href"]) for link in li_element.select("a[href]")],
    )


def remove_parenthesized(text):
    return "".join(_remove_parenthesized(text))


def _remove_parenthesized(text):
    paren_depth = 0
    for curr, next in _pairs(text):
        if curr == "(":
            paren_depth += 1
        elif curr == ")" and paren_depth > 0:
            paren_depth -= 1
        elif curr == " " and next == "(":
            pass
        elif curr == "\n" and next == "\n":
            paren_depth = 0
            yield curr
        elif paren_depth > 0:
            pass
        else:
            yield curr


def _pairs(text):
    for idx in range(len(text)):
        first = text[idx]
        if idx + 1 < len(text):
            yield (first, text[idx + 1])
        else:
            yield (first, None)


def path_final(url):
    return url.split("/")[-1]


def collapse(string):
    return re.sub(r"\s+", " ", string)
