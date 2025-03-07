import behave as bhv

import requests
from inputs import SHOW_ID
import json
import email

import data as d

@bhv.then("Wikipedia articles about {topic} are retrieved")
def article_fetches(context, topic):
    for title in context.topics[topic].articles:
        response = requests.post(
            f"{context.prop.wikipedia.url}/__admin/requests/find",
            json={
                "urlPath": "/w/api.php",
                'queryParameters': {
                    'page': {'equalTo': title},
                }

            },
        )
        response.raise_for_status()
        assert len(response.json()["requests"]) >= 1, (response.json(), title)

@bhv.then("headlines are retrieved from Wikipedia")
def headline_fetch(context):
    response = requests.post(
        f"{context.prop.wikipedia.url}/__admin/requests/find",
        json={
            "method": "GET",
            "urlPath": "/w/api.php",
            "queryParameters": {
                "action": {"equalTo": "parse"},
                "format": {"equalTo": "json"},
                "prop": {"equalTo": "text|revid"},
                "page": {"equalTo": "Template:In_the_news"},
                "section": {"equalTo": "0"},
            },
        },
    )
    response.raise_for_status()
    assert len(response.json()["requests"]) == 1, response.json()

@bhv.then("the episode list from Spreaker is retrieved")
def episode_fetches(context):
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "GET",
            'urlPath': f"/v2/shows/{SHOW_ID}/episodes",
            "queryParameters": {
                "filter": {"equalTo": "editable"},
                "sorting": {"equalTo": "oldest"},
            },
        },
    )
    response.raise_for_status()
    reqs = response.json()["requests"]
    assert len(reqs) == 1, response.json()
    assert reqs[0]['headers']["Authorization"] == "Bearer DUMMY_TOKEN"

@bhv.then("a script about {topic} is sent for text-to-speech processing")
def tts_processing(context, topic):
    news = context.topics[topic]
    possible = {"INTRO", "OUTRO", news.headline_plain}
    possible.update({
        p.strip() for article in news.articles.values()
            for p in article.plain.split("\n\n")
    })
    response = requests.post(
        f"{context.prop.google.url}/__admin/requests/find",
        json={ "method": "POST", "urlPath": "/v1/text:synthesize" }
    )
    response.raise_for_status()
    payload = json.loads(response.json()["requests"][0]["body"])
    text = payload["input"]["text"]
    assert len(text) <= int(context.prop.tts.length_limit), text
    actual = {p.strip() for p in text.split("\n\n")}
    assert len(actual) > 0, actual
    assert 0 == len(actual.difference(possible)), (
        actual, possible, actual.difference(possible))

@bhv.then("no scripts are sent for text-to-speech processing")
def no_tts_processing(context):
    response = requests.post(
        f"{context.prop.google.url}/__admin/requests/find",
        json={ "method": "POST", "urlPath": "/v1/text:synthesize" }
    )
    response.raise_for_status()
    captured = response.json()["requests"]
    assert captured == [], captured

@bhv.then("an episode about {topic} is uploaded to Spreaker")
def spreaker_upload(context, topic):
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "POST",
            "urlPath": f"/v2/shows/{SHOW_ID}/episodes",
        }
    )
    response.raise_for_status()
    captured = response.json()["requests"][0]
    headers = captured["headers"]

    assert headers["Authorization"] == "Bearer DUMMY_TOKEN", headers

    msg = email.message_from_string(
        f"Content-Type: {headers["Content-Type"]}\n{captured["body"]}"
        )
    fields = {
        part.get_param(
            "name", header="Content-Disposition"): part.get_payload()
            for part in msg.get_payload() }
    assert fields["media_file"] == 'foo', msg # from BASE_64_MP3
    assert "CC BY-SA 4.0" in fields["description"], msg
    assert fields["title"] == context.topics[topic].headline_plain, (msg, context)

@bhv.then("no episodes are uploaded to Spreaker")
def spreaker_upload(context):
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "POST",
            "urlPath": f"/v2/shows/{SHOW_ID}/episodes",
        }
    )
    response.raise_for_status()
    captured = response.json()["requests"]
    assert captured == [], captured

@bhv.then("the episode about {topic} is deleted")
def spreaker_deleted(context, topic):
    lookup = {episode.topic: id for id, episode in
        enumerate(d.episodes(context))}

    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "DELETE",
            "urlPath": f"/v2/episodes/{lookup[topic]}",
        },
    )
    response.raise_for_status()
    recorded = response.json()["requests"]
    assert len(recorded) == 1, response.json()
    assert recorded[0]['headers']["Authorization"] == "Bearer DUMMY_TOKEN"

@bhv.then("the episode about {topic} is kept")
def spreaker_deleted(context, topic):
    lookup = {episode.topic: id for id, episode in
        enumerate(d.episodes(context))}

    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "DELETE",
            "urlPath": f"/v2/episodes/{lookup[topic]}",
        },
    )
    response.raise_for_status()
    assert response.json()["requests"] == [], response
