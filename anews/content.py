#! /usr/bin/env python3

"""Hacky and non-portable script to get info from Wikipedia.

"""


from bs4 import BeautifulSoup
import wikipedia
import re
import collections

# Portal:Current events/Headlines
IN_THE_NEWS_ID = "5779344"

# How many articles into the past to remember
# to avoid repeats
SEEN_ARTICLES_COUNT = 100
# file where that info is saved
SEEN_ARTICLES_FILE = "seen_articles.txt"

SEPARATOR = '\n---\n'

INTRO = """
This is Artificial News, where a computer reads from Wikipedia.

I am a computer.  My pronunciation is sometimes wrong.  News and
information in this show comes from Wikipedia and is not guaranteed to
be correct.
""".strip()

CLOSING = """
This episode of Artificial News is now over.

I am a computer.  My pronunciation is sometimes wrong.  News and
information in this show comes from Wikipedia and is not guaranteed to
be correct.

For more information on this show, including content licensing
information, go to
bee, jay, a, are, ee, ess, ess, dot com / news.
That's
Bravo,
Juliette,
Alpha,
Romeo,
Echo,
Sierra,
Sierra,
dot com / news.

Thank you for listening.
""".strip()

class Headline:
    def __init__(self, elem):
        self.headline = elem.text.strip()
        # Sometimes more than one bolded link
        link_elems = elem(
                lambda tag: tag.name == "a" and tag.parent.name == "b")
        self.links = { link.attrs['href'] : link.attrs['title']
                for link in link_elems }
        self.text = None

    def unseen(self, seen):
        return set(self.links.keys()).difference(seen)

    def article_text(self):
        if self.text == None and len(self.links) > 0:
            parts = [formatted(self.headline)]

            for href, title in self.links.items():
                page = wikipedia.page(title=title,
                        auto_suggest=True, redirect=True)
                text = None
                if '#' in href:
                    section = href.split('#')[-1]
                    section = re.sub('_', ' ', section)
                    text = page.section(section)
                if text == None or len(text.strip()) == 0:
                    text = page.summary
                parts.append(formatted(text))

            self.text = '\n\n'.join(parts)
        return self.text

def formatted(article_text):
    def stream_process(text):
        paren_depth = 0
        for char in text:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '\n':
                # The original text uses single newlines for paragraph
                # breaks, fix that.
                yield '\n\n'
                paren_depth = 0
            elif paren_depth <= 0:
                yield char
            else:
                # For now, omit anything in parentheses
                # We might do something more sophisticated later, but
                # parenthesized info is usually something unnecessary
                # that the text-to-speech handles poorly.
                pass

    return ''.join(stream_process(article_text))

def main():
    seen_articles = load_seen()

    wikipedia.set_rate_limiting(True)
    in_the_news = wikipedia.page(pageid=IN_THE_NEWS_ID)
    soup = BeautifulSoup(in_the_news.html())

    headlines = (Headline(elem) for elem in soup.find_all('li'))

    print(INTRO)

    for headline in headlines:
        if headline.unseen(seen_articles):
            print(SEPARATOR)
            print(headline.article_text())
            seen_articles.extend(headline.unseen(seen_articles))

    print(SEPARATOR)
    print(CLOSING)

    save_seen(seen_articles)


def load_seen():
    """Track most recent articles between runs to avoid repeats."""
    seen_articles = collections.deque([], SEEN_ARTICLES_COUNT)
    try:
        with open(SEEN_ARTICLES_FILE, 'r') as seen_file:
            for line in seen_file:
                seen_articles.append(line.strip())
    except FileNotFoundError:
        # Just create the file later if it doesn't exist
        pass
    return seen_articles


def save_seen(seen_articles):
    """Track most recent articles between runs to avoid repeats."""
    with open(SEEN_ARTICLES_FILE, 'w') as seen_file:
        for article in seen_articles:
            print(article, file=seen_file)


if __name__ == '__main__':
    main()

