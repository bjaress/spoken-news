SEPARATOR = "\n\n"


def extract_plan(wikipedia_client, headline):
    summaries = {}
    for title in set(headline.articles):
        summaries[title] = wikipedia_client.summary(title).split("\n\n")
    return Plan(summaries)


class Plan:
    def __init__(self, summaries):
        self.summaries = summaries

    def text(self, max_chars):
        paragraphs = []
        budget = max_chars
        for title in sorted(self.summaries.keys(), key=sort_key, reverse=True):
            head, *tail = self.summaries[title]
            paragraphs, budget = include_if_room(paragraphs, budget, [head])
            paragraphs, budget = include_if_room(paragraphs, budget, tail)
        return SEPARATOR.join(paragraphs)


def include_if_room(paragraphs, budget, additional_paragraphs, len_sep=len(SEPARATOR)):
    separators = len(additional_paragraphs)
    if paragraphs == [] and additional_paragraphs != []:
        separators -= 1
    cost = separators * len_sep + sum(len(p) for p in additional_paragraphs)
    if cost > budget:
        return paragraphs, budget
    return paragraphs + additional_paragraphs, budget - cost


def sort_key(title):
    return (len(title.split()), len(title), title)
