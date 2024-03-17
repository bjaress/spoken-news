import behave as bhv
import data as d

import textwrap
import random

@bhv.given("there is a simple news item about frogs")
def news_frogs(context):
    d.topics(context)["frogs"] = d.NewsItem(
        headline_html="""A <a href='/wiki/Frog'>frog</a> said hi.""",
        headline_plain="""A frog said hi.""",
        Frog=d.Article(
            markup="""A frog is a type of animal.""",
            plain="""A frog is a type of animal.""",
        ),
    )
    d.sync(context)

@bhv.given("there is a news item about bananas that links to a section")
def news_bananas(context):
    d.topics(context)["bananas"] = d.NewsItem(
        headline_html="""A <a href='/wiki/Fruit#Banana'>banana</a> said hi.""",
        headline_plain="""A banana said hi.""",
        Fruit=d.Article(
            markup=textwrap.dedent("""
            Don't include this sentence.
            ==Banana==
            Banana peels are slippery.
            """),
            plain="""Banana peels are slippery.""",
        ),
    )
    d.sync(context)

@bhv.given("there is a news item with very long articles about sports")
def news_sports(context):
    title_limit = int(context.prop.spreaker.title_limit)
    script_limit = int(context.prop.tts.length_limit)
    headline_filler = " ".join(["yada"] * title_limit)

    def article_filler(text, length):
        population = [char for char in text] + [" ", "\n\n"]
        weights = [20] * len(text) + [40, 1]
        return "".join(random.choices(population, k=length, weights=weights))

    article_length = script_limit // 3 * 2
    football_filler = article_filler("football", article_length)
    baseball_filler = article_filler("baseball", article_length)

    d.topics(context)["sports"] = d.NewsItem(
        headline_html=f"""<a href='/wiki/Baseball'>baseball</a>
            <a href='/wiki/American_Football'>football</a> {headline_filler}""",
        headline_plain=(
            f"baseball football {headline_filler}"[:title_limit - 3] + "..."),
        Baseball=d.Article(
            markup=baseball_filler,
            plain=baseball_filler,
        ),
        American_Football=d.Article(
            markup=football_filler,
            plain=football_filler,
        ),
    )
    d.sync(context)


@bhv.given("there is a {age_days:d} day old episode about {topic}")
def old_episode(context, age_days, topic):
    d.episodes(context).append(d.ExistingEpisode(
        title=f"A {topic} said hi.",
        age_days=age_days,
        topic=topic))
    d.sync(context)
