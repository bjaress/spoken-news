import requests
import re
from api import models
from api import similar
from bs4 import BeautifulSoup
from urllib import parse
import html_sanitizer
import html2text

import logging

API_PATH = "/w/api.php"
PAGE_PATH = "/w/rest.php/v1/page"
PERMALINK_PATH = "/w/index.php"

LICENSE_NOTICE = """
Created from parts of Wikipedia articles and available under the CC
BY-SA 4.0 license: https://creativecommons.org/licenses/by-sa/4.0/
"""


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.config = config

        ht = html2text.HTML2Text()
        ht.ignore_emphasis = True
        ht.ignore_links = True
        ht.ignore_images = True
        ht.ul_item_mark = "-"
        ht.unicode_snob = True
        self.html2text = ht

    def headlines(self):
        soup, _ = self.fetch_html(self.config.headlines_page)

        headlines = [extract_headline(item) for item in soup.ul.find_all("li")]
        return headlines

    def fetch_html(self, title, id=0):
        response = self.requests.get(
            f"{self.config.url}{API_PATH}",
            params={
                "action": "parse",
                "redirects": "",
                "section": id,
                "prop": "text|revid",
                "format": "json",
                "page": title,
            },
        )
        logging.info(f"Wikipedia Request: {response.status_code}")
        response.raise_for_status()
        parse = response.json()["parse"]
        html = parse["text"]["*"]
        html = html_sanitizer.Sanitizer().sanitize(html)
        soup = BeautifulSoup(html, "html.parser")
        return soup, parse["revid"]

    def section_index_for_reference(self, reference):
        if reference.section is None or len(reference.section) == 0:
            return 0
        response = self.requests.get(
            f"{self.config.url}{API_PATH}",
            params={
                "action": "parse",
                "prop": "sections",
                "format": "json",
                "page": reference.title,
            },
        )
        logging.info(f"Wikipedia Request: {response.status_code}")
        response.raise_for_status()

        for section in response.json()["parse"]["sections"]:
            if section["linkAnchor"] == reference.section:
                return section["index"]
        return 0

    def fetch_and_parse_article(self, article_reference):
        soup, version = self.fetch_html(
            article_reference.title,
            self.section_index_for_reference(article_reference),
        )
        return models.Article(
            summary=self.extract_text_chunks(soup),
            permalink_id=version,
            reference=article_reference,
        )

    def extract_text_chunks(self, soup):
        selector = ":is(p, ol, ul, dl, blockquote):not(:is(p, ol, ul, dl, blockquote, table) *)"
        past_boilerplate = False
        result = []
        for elem in soup.select(selector):
            # skip references at end
            if len(elem.select('a[href*="cite_ref-"]')):
                continue
            # remove metadata
            for cite in elem.select('a[href*="cite_note-"], a[href*=":"]'):
                cite.clear()
            # skip to first real paragraph
            if elem.name == "p" and "." in " ".join(elem.strings):
                past_boilerplate = True
            elif not past_boilerplate:
                continue

            text = self.html2text.handle(str(elem)).removesuffix("\n\n")
            if text.startswith("Cite error:"):
                continue

            result.append(remove_parenthesized(text))
        return result

    def describe(self, story):
        notice = " ".join(LICENSE_NOTICE.split())
        parts = notice, *(
            permalink(f"{self.config.url}{PERMALINK_PATH}", reference.title, id)
            for id, reference in story.permalink_ids().items()
        )
        return "\n".join(parts)


def permalink(base, title, id):
    parts = parse.urlparse(base)
    parts = parts._replace(
        query=parse.urlencode(
            {
                "title": title,
                "oldid": id,
            },
            quote_via=parse.quote,
            safe="",
        )
    )
    return parse.urlunparse(parts)


def extract_headline(li_element):
    return models.Headline(
        text=remove_parenthesized(collapse(li_element.text)),
        articles=[
            reference_from_url(link["href"]) for link in li_element.select("a[href]")
        ],
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


def reference_from_url(url):
    parsed = parse.urlparse(url)
    return models.ArticleReference(
        title=parsed.path.split("/")[-1],
        section=parsed.fragment,
    )


def collapse(string):
    return re.sub(r"\s+", " ", string)


if __name__ == "__main__":
    import sys

    class DummyConfig:
        def __init__(self, wikipedia_url):
            self.url = wikipedia_url

    page_url = sys.argv[1]
    client = Client(DummyConfig("https://en.wikipedia.org"))
    article = client.fetch_and_parse_article(reference_from_url(page_url))
    print(f"{article.reference} {article.permalink_id}")
    print("\n\n".join(article.summary))
