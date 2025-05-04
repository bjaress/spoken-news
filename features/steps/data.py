import behave as bhv

import datetime
import requests
import time
import random
from inputs import SHOW_ID

BASE_64_MP3 = "Zm9v" #foo


def sync(context):
    sync_headlines(context)
    sync_articles(context)
    sync_existing_episodes(context)
    mp3(context)

def sync_existing_episodes(context):
    today = datetime.date.fromisoformat(context.prop.TODAY)
    items = [ { 'title': episode.title
              , 'published_at':
                  f"{today - datetime.timedelta(days=episode.age_days)} 00:00:00"
              , 'episode_id': id
              } for id, episode in enumerate(episodes(context))]
    data = {
        'request': {
            'urlPath': f"/v2/shows/{SHOW_ID}/episodes",
        },
        'response': {
            'status': 200,
            'jsonBody': {
                'response': {
                    'items': items
                },
            },
        },
    }
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/mappings", json=data
    )
    response.raise_for_status()

def sync_articles(context):
    for news_item in context.topics.values():
        for title, article in news_item.articles.items():
            data = {
                'request': {
                    'urlPath': "/w/api.php",
                    'queryParameters': {
                        'page': {'equalTo': title},
                        'action': {'equalTo': 'parse'},
                        'prop': {'equalTo': 'text|revid'},
                        'format': {'equalTo': 'json'},
                        'section': {'equalTo':
                            '0' if article.section_title is None else '1'
                        },
                        'redirects': {'equalTo': ''},
                    }
                },
                'response': {
                    'status': 200,
                    'jsonBody': {
                        "parse": {
                            'pageid': article.id,
                            'revid': article.id + '0000',
                            'text': {"*": article.html},
                        },
                    },
                }
            }
            response = requests.post(
                f"{context.prop.wikipedia.url}/__admin/mappings", json=data
            )
            response.raise_for_status()

            if article.section_title is None:
                continue
            data = {
                'request': {
                    'urlPath': "/w/api.php",
                    'queryParameters': {
                        'page': {'equalTo': title},
                        'action': {'equalTo': 'parse'},
                        'prop': {'equalTo': 'sections'},
                        'format': {'equalTo': 'json'},
                    }
                },
                'response': {
                    'status': 200,
                    'jsonBody': {
                        "parse": {
                            'sections': [{
                                "index": '1',
                                "linkAnchor": article.section_title,
                            }],
                        },
                    },
                }
            }
            response = requests.post(
                f"{context.prop.wikipedia.url}/__admin/mappings", json=data
            )
            response.raise_for_status()


def sync_headlines(context):
    data = {
        "request": {
            "urlPath": "/w/api.php",
            "queryParameters": {"page": {"equalTo": "Template:In_the_news"}},
        },
        "response": {
            "status": 200,
            "jsonBody": {
                "parse": {
                    "title": "Template:In the news",
                    "revid": 482256,
                    "text": {"*": headlines_html(context)},
                }
            },
        },
    }
    response = requests.post(
        f"{context.prop.wikipedia.url}/__admin/mappings", json=data
    )
    response.raise_for_status()


def headlines_html(context):
    news_inner = "</li><li>".join(
        item.headline_html for item in topics(context).values() if item.type == "news")
    deaths_inner = "</li><li>".join(
        item.headline_html for item in topics(context).values() if item.type == "death")
    return f"""
        <div><ul><li>{news_inner}</li></ul></div>
        <div>
          <b><a href="/wiki/Deaths_in_1776" title="Deaths in 2049">Recent deaths</a></b>:
          <link href="mw-data:TemplateStyles:r1129693374" rel="mw-deduplicated-inline-style"/>
          <div class="hlist inline">
            <ul>
              <li>{deaths_inner}</li>
            </ul>
          </div>
        </div>
        """



def topics(context):
    if not hasattr(context, "topics"):
        context.topics = {}
    return context.topics

def episodes(context):
    if not hasattr(context, "episodes"):
        context.episodes = []
    return context.episodes

def mp3(context):
    data = {
        "request": {
            "urlPath": "/v1/text:synthesize"
        },
        "response": {
            "status": 200,
            "jsonBody": {
                "audioContent": BASE_64_MP3
            },
        },
    }
    response = requests.post(
        f"{context.prop.google.url}/__admin/mappings", json=data
    )
    response.raise_for_status()


class NewsItem:
    def __init__(self, headline_html, headline_plain, type="news", **articles):
        self.headline_html = headline_html
        self.headline_plain = headline_plain
        self.articles = articles
        self.type = type

class Article:
    def __init__(self, plain, html, section_title=None):
        self.plain = plain
        self.html = html
        self.section_title = section_title
        self.id = str(random.randint(1, 2**30))

class ExistingEpisode:
    def __init__(self, title, age_days, topic):
        self.title = title
        self.age_days = age_days
        self.topic = topic
