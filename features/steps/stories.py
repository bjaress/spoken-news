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
            plain="""A frog is a type of animal.""",
            html="""<p>A frog is a type of animal.</p>""",
        ),
    )
    d.sync(context)

@bhv.given("there is a news item about bananas that links to a section")
def news_bananas(context):
    d.topics(context)["bananas"] = d.NewsItem(
        headline_html="""A <a href='/wiki/Fruit#Banana'>banana</a> said hi.""",
        headline_plain="""A banana said hi.""",
        Fruit=d.Article(
            html="""
            <h3>Peels</h3>
            <p>Banana peels are slippery.</p>
            """,
            section_title = "Banana",
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
        count = length // len(text)
        return f"{text}. {"\n\n".join([text] * count)}"

    article_length = script_limit // 3 * 2
    football_filler = article_filler("football", article_length)
    baseball_filler = article_filler("baseball", article_length)

    d.topics(context)["sports"] = d.NewsItem(
        headline_html=f"""<a href='/wiki/Baseball'>baseball</a>
            <a href='/wiki/American_Football'>football</a> {headline_filler}""",
        headline_plain=(
            f"baseball football {headline_filler}"[:title_limit - 3] + "..."),
        Baseball=d.Article(
            plain=baseball_filler,
            html="<p>" + baseball_filler.replace("\n\n", "</p><p>") + "</p>",
        ),
        American_Football=d.Article(
            plain=football_filler,
            html="<p>" + football_filler.replace("\n\n", "</p><p>") + "</p>",
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
