import requests
import base64
import random
import collections

# https://cloud.google.com/text-to-speech/docs/basics

import logging

import api.error


class VoiceProfile:
    def __init__(self, name, language):
        self.name = name
        self.language = language

    def payload(self, text):
        return {
            "input": {"text": text},
            "voice": {
                "name": self.name,
                "languageCode": self.language,
            },
            "audioConfig": {
                "audioEncoding": "MP3",
            },
        }

    def __str__(self):
        return f"VoiceProfile({self.name}, {self.language})"


# Completely arbitrary use of fibonacci numbers
#
# This is absolutely favoritism, but people in certain places are more
# likely to find the podcast, and English is mostly a second language in
# India.
LANGUAGES = {
    "en-US": 13,
    "en-GB": 8,
    "en-AU": 5,
    "en-IN": 3,
}

PERSONALITIES = [
    "Achernar",
    "Achird",
    "Algenib",
    "Algieba",
    "Alnilam",
    "Aoede",
    "Autonoe",
    "Callirrhoe",
    "Charon",
    "Despina",
    "Enceladus",
    "Erinome",
    "Fenrir",
    "Gacrux",
    "Iapetus",
    "Kore",
    "Laomedeia",
    "Leda",
    "Orus",
    "Pulcherrima",
    "Puck",
    "Rasalgethi",
    "Sadachbia",
    "Sadaltager",
    "Schedar",
    "Sulafat",
    "Umbriel",
    "Vindemiatrix",
    "Zephyr",
    "Zubenelgenubi",
]


def pick_voice(languages=LANGUAGES, personalities=PERSONALITIES, random=random):
    lang = random.choices(
        list(languages.keys()),
        list(languages.values()),
        k=1,
    )[0]

    person = random.choice(personalities)

    return VoiceProfile(f"{lang}-Chirp3-HD-{person}", lang)


class Client:
    def __init__(self, config, requests=requests, pick_voice=pick_voice):
        self.requests = requests
        self.url = f"{config.server}/v1/text:synthesize?key={config.api_key}"
        self.config = config
        self.voice = pick_voice()

    def speak(self, story):
        logging.info(self.voice)
        response = self.requests.post(
            url=self.url,
            json=self.voice.payload(story.text(self.config)),
        )
        api.error.check_response(response)
        return base64.b64decode(response.json()["audioContent"])
