import wikipediaapi
from api import models
from bs4 import BeautifulSoup

HEADLINE_PAGE = "Template:In_the_news"

class Client:
    def __init__(self, wikipediaapi=wikipediaapi):
        self.external = wikipediaapi
        self.html = self.external.Wikipedia(
            language='en',
            extract_format=self.external.ExtractFormat.HTML)

    def headlines(self):
        summary = self.html.page(HEADLINE_PAGE).summary

        soup = BeautifulSoup(summary, 'html.parser')
        return [parse_headline(element) for element in soup.find_all('li')]


def parse_headline(li_element):
    headline = models.Headline(text=li_element.text.strip())
    return headline


