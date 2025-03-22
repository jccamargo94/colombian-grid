import httpx


class HTTPClient:
    def __init__(self):
        self.client = httpx.Client()

    def get(self, url: str):
        return self.client.get(url)

    def close(self):
        self.client.close()
