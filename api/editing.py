def extract_plan(wikipedia_client, headline):
    summaries = {}
    for title in set(headline.articles):
        summaries[title] = wikipedia_client.summary(title).split("\n\n")
    return Plan(summaries)


class Plan:
    def __init__(self, summaries):
        self.summaries = summaries

    def text(self):
        paragraphs = []
        for title in sorted(self.summaries.keys(), key=sort_key, reverse=True):
            for paragraph in self.summaries[title]:
                paragraphs.append(paragraph)
        return "\n\n".join(paragraphs)


def sort_key(title):
    return (len(title.split()), len(title), title)
