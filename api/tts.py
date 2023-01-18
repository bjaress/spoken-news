import requests


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.url = f"{config['server']}/v1/text:synthesize?key={config['api_key']}"

    def speak(self, words):
        self.requests.post(
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
