import re

SEPARATOR = "\n\n"


def extract_story(wikipedia_client, headline):
    return Story(
        headline.text,
        [
            wikipedia_client.fetch_and_parse_article(reference)
            for reference in headline.articles
        ],
    )


class Story:
    def __init__(self, headline, articles):
        self.articles = articles
        self.headline = headline

    def text(self, tts_config):
        reserve = bytecount(SEPARATOR) + bytecount(tts_config.outro)
        budget = tts_config.length_limit - reserve
        paragraphs, budget = include_if_room([], budget, [tts_config.intro])
        paragraphs, budget = include_if_room(paragraphs, budget, [self.headline])

        for article in sorted(self.articles, key=sort_key, reverse=True):
            head, *tail = article.summary
            paragraphs, budget = include_if_room(paragraphs, budget, [head])
            paragraphs, budget = include_if_room(paragraphs, budget, tail)

        paragraphs, budget = include_if_room(
            paragraphs, budget + reserve, [tts_config.outro]
        )
        return SEPARATOR.join(paragraphs)

    def permalink_ids(self):
        return {article.permalink_id: article.reference for article in self.articles}


def bytecount(text):
    return len(text.encode())


def include_if_room(
    paragraphs, budget, additional_paragraphs, len_sep=bytecount(SEPARATOR)
):
    separators = len(additional_paragraphs)
    # There's a separator we don't need if we adding to an empty list
    if paragraphs == [] and additional_paragraphs != []:
        separators -= 1
    cost = separators * len_sep + sum(bytecount(p) for p in additional_paragraphs)
    if cost > budget:
        return paragraphs, budget
    return paragraphs + additional_paragraphs, budget - cost


def sort_key(article):
    title = article.reference.title
    title_parts = re.split(r"[_\W]+", title)

    # Prioritize and de-prioritize some Wikipedia articles
    normal = not (title_parts[:2] == ["List", "of"])
    rank = normal + article.reference.featured

    return (rank, len(title_parts), len(title), title)
