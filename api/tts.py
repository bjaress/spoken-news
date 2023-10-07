import requests
import base64
import random

# https://cloud.google.com/text-to-speech/docs/basics

import logging

import api.error


class VoiceProfile:
    def __init__(self, name, language, speed, pitch):
        self.name = name
        self.language = language
        self.speed = speed
        self.pitch = pitch

    def payload(self, text):
        return {
            "input": {"text": text},
            "voice": {
                "name": self.name,
                "languageCode": self.language,
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": self.speed,
                "pitch": self.pitch,
            },
        }


VOICES = [
    VoiceProfile("en-AU-Neural2-B", "en-au", 0.84, -5.20),
    VoiceProfile("en-AU-Neural2-C", "en-au", 0.85, -5.20),
    VoiceProfile("en-GB-Neural2-B", "en-gb", 0.85, -5.20),
    VoiceProfile("en-GB-Neural2-C", "en-gb", 0.90, -5.20),
    VoiceProfile("en-US-Neural2-F", "en-us", 0.85, -5.20),
    VoiceProfile("en-US-Neural2-J", "en-us", 0.85, -5.20),
]


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.url = f"{config.server}/v1/text:synthesize?key={config.api_key}"
        self.config = config

    def speak(self, story):
        response = self.requests.post(
            url=self.url,
            json=random.choice(VOICES).payload(story.text(self.config)),
        )
        api.error.check_response(response)
        return base64.b64decode(response.json()["audioContent"])
