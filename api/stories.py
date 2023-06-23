SEPARATOR = "\n\n"


def extract_story(wikipedia_client, headline):
    summaries = {}
    for title in set(headline.articles):
        summaries[title] = wikipedia_client.summary(title).split("\n\n")
    return Story(summaries)


class Story:
    def __init__(self, summaries):
        self.summaries = summaries

    def text(self, tts_config):
        reserve = bytecount(SEPARATOR) + bytecount(tts_config.outro)
        budget = tts_config.length_limit - reserve
        paragraphs, budget = include_if_room([], budget, [tts_config.intro])

        for title in sorted(self.summaries.keys(), key=sort_key, reverse=True):
            head, *tail = self.summaries[title]
            paragraphs, budget = include_if_room(paragraphs, budget, [head])
            paragraphs, budget = include_if_room(paragraphs, budget, tail)

        paragraphs, budget = include_if_room(
            paragraphs, budget + reserve, [tts_config.outro]
        )
        return SEPARATOR.join(paragraphs)


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
