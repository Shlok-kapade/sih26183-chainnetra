import json
import os
from typing import Any, Dict, Optional

import httpx

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "fixtures")

def get_fixture_path(provider: str, identifier: str) -> str:
    return os.path.join(FIXTURE_DIR, f"{provider}_{identifier}.json")

def load_fixture(provider: str, identifier: str) -> Optional[Dict[str, Any]]:
    path = get_fixture_path(provider, identifier)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_fixture(provider: str, identifier: str, data: Dict[str, Any]) -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    path = get_fixture_path(provider, identifier)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class FixtureTransport(httpx.AsyncBaseTransport):
    def __init__(self, provider: str, identifier: str):
        self.provider = provider
        self.identifier = identifier

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        data = load_fixture(self.provider, self.identifier)
        if data is None:
            return httpx.Response(404, text="Fixture not found")
        return httpx.Response(200, json=data, request=request)
