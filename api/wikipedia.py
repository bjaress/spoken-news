import requests
import re
from api import models
from api import similar
from bs4 import BeautifulSoup
import wikitextparser as wtp
from urllib import parse

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

    def fetch_article(self, article_reference):
        title = article_reference.title
        response = self.requests.get(f"{self.config.url}{PAGE_PATH}/{title}")
        json = response.json()
        parsed = wtp.parse(json["source"])
        text = section_text(article_reference.section, parsed.get_sections())
        return models.Article(
            summary=remove_parenthesized(text).strip(),
            permalink_id=json["latest"]["id"],
            reference=article_reference,
        )

    def describe(self, story):
        notice = " ".join(LICENSE_NOTICE.split())
        parts = notice, *(
            permalink(reference.title, id)
            for id, reference in story.permalink_ids().items()
        )
        return "\n".join(parts)


def permalink(title, id):
    return f"https://en.wikipedia.org/w/index.php?title={title}&oldid={id}"


def extract_headline(li_element):
    return models.Headline(
        text=remove_parenthesized(collapse(li_element.text)),
        articles=[
            reference_from_url(link["href"]) for link in li_element.select("a[href]")
        ],
    )


def section_text(section_name, sections):
    best = sections[0]
    best_score = 0
    for section in sections:
        if section.title is None or section_name is None or len(section_name) == 0:
            continue
        score = similar.score(section.title, section_name)
        if score > best_score:
            best, best_score = section, score

    # omit references
    for ref in best.get_tags("ref"):
        ref.contents = ""
    # omit header of section
    return wtp.parse(best.contents).plain_text()


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


def reference_from_url(url):
    parsed = parse.urlparse(url)
    return models.ArticleReference(
        title=parsed.path.split("/")[-1],
        section=parsed.fragment,
    )


def collapse(string):
    return re.sub(r"\s+", " ", string)
