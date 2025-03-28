import requests
import base64
import random

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


VOICES = [
    VoiceProfile("en-US-Chirp3-HD-Aoede", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Charon", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Fenrir", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Kore", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Leda", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Orus", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Puck", "en-US"),
    VoiceProfile("en-US-Chirp3-HD-Zephyr", "en-US"),
    VoiceProfile("en-GB-Chirp3-HD-Aoede", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Charon", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Fenrir", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Kore", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Leda", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Orus", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Puck", "en-GB"),
    VoiceProfile("en-GB-Chirp3-HD-Zephyr", "en-GB"),
    VoiceProfile("en-AU-Chirp3-HD-Aoede", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Charon", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Fenrir", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Kore", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Leda", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Orus", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Puck", "en-AU"),
    VoiceProfile("en-AU-Chirp3-HD-Zephyr", "en-AU"),
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
