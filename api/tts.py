import requests
import base64

# https://cloud.google.com/text-to-speech/docs/basics

import logging


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.url = f"{config['server']}/v1/text:synthesize?key={config['api_key']}"

    def speak(self, words):
        response = self.requests.post(
            url=self.url,
            json={
                "input": {"text": words},
                "voice": {
                    "languageCode": "en-gb",
                    "name": "en-GB-Standard-A",
                    "ssmlGender": "FEMALE",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            },
        )
        logging.info(f"TTS Request: {response.status_code}")
        logging.debug(str(response)[:20])
        return base64.b64decode(response.json()["audioContent"])
