import behave as bhv
import requests

SHOW_ID = 1234

@bhv.when("it is time to generate news")
def trigger_app(context):
    response = requests.post(context.prop.app.url, json= {
      "message": {
        "attributes": {
          "spreaker_url": context.prop.spreaker.url,
          "spreaker_token": "DUMMY_TOKEN",
          "spreaker_show_id": SHOW_ID,
          "spreaker_title_limit": int(context.prop.spreaker.title_limit),
          "spreaker_age_limit": 30,
          "spreaker_publish_delay_minutes": 60 * 24,
          "tts_api_key": "DUMMY_KEY",
          "tts_server": context.prop.google.url,
          "tts_length_limit": int(context.prop.tts.length_limit),
          "tts_intro": "INTRO",
          "tts_outro": "OUTRO",
          "wikipedia_url": context.prop.wikipedia.url,
          "wikipedia_headlines_page": "Template:In_the_news",
          "wikipedia_polite_delay": 0,
        },
        "messageId": "blahblah"
      },
      "subscription": "blah/blah/blah"
    })
    response.raise_for_status()

@bhv.when("it is time to clean up episodes older than {age_days:d} days")
def cleanup(context, age_days):
    response = requests.post(f"{context.prop.app.url}/cleanup", json= {
      "message": {
        #spreaker only
        "attributes": {
        "url": context.prop.spreaker.url,
        "token":  "DUMMY_TOKEN",
        "show_id":  SHOW_ID,
        "title_limit":  context.prop.spreaker.title_limit,
        "age_limit":  age_days,
        "publish_delay_minutes": 60 * 24,
        },
        "messageId": "blahblah"
      },
      "subscription": "blah/blah/blah"
    })
    response.raise_for_status()
