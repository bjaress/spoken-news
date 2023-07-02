SEPARATOR = "\n\n"


def extract_story(wikipedia_client, headline):
    articles = {}
    for title in set(headline.articles):
        articles[title] = wikipedia_client.fetch_article(title)
    return Story(headline.text, articles)


class Story:
    def __init__(self, headline, articles):
        self.articles = articles
        self.headline = headline

    def text(self, tts_config):
        reserve = bytecount(SEPARATOR) + bytecount(tts_config.outro)
        budget = tts_config.length_limit - reserve
        paragraphs, budget = include_if_room([], budget, [tts_config.intro])
        paragraphs, budget = include_if_room(paragraphs, budget, [self.headline])

        for title in sorted(self.articles.keys(), key=sort_key, reverse=True):
            head, *tail = self.articles[title].summary.split("\n\n")
            paragraphs, budget = include_if_room(paragraphs, budget, [head])
            paragraphs, budget = include_if_room(paragraphs, budget, tail)

        paragraphs, budget = include_if_room(
            paragraphs, budget + reserve, [tts_config.outro]
        )
        return SEPARATOR.join(paragraphs)

    def permalink_ids(self):
        return {title: article.permalink_id for title, article in self.articles.items()}


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


def sort_key(title):
    return (len(title.split()), len(title), title)
