"""
Low-level Twitch API access:
- OAuth token
- GET requests with retry
"""

import asyncio
from typing import List, Optional, Dict

import aiohttp

from twitch_checker.config import CLIENT_ID, CLIENT_SECRET


TOKEN_URL = "https://id.twitch.tv/oauth2/token"
HELIX_URL = "https://api.twitch.tv/helix/"


class TwitchAPI:
    """Handles raw Twitch API communication with token refresh and retry."""

    def __init__(self, client_id: str = CLIENT_ID, client_secret: str = CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        self._session_lock = asyncio.Lock()

    async def ensure_session(self) -> None:
        if self.session is None or self.session.closed:
            async with self._session_lock:
                if self.session is None or self.session.closed:
                    self.session = aiohttp.ClientSession()

    async def fetch_token(self) -> str:
        await self.ensure_session()
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        async with self.session.post(TOKEN_URL, params=params) as res:
            data = await res.json()

        if "access_token" not in data:
            raise RuntimeError(f"Failed to obtain Twitch token: {data}")

        self.token = data["access_token"]
        return self.token

    async def _get(self, endpoint: str, params: List[tuple], retry: int = 1) -> dict:
        await self.ensure_session()

        if not self.token:
            await self.fetch_token()

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.token}",
        }

        async with self.session.get(HELIX_URL + endpoint, headers=headers, params=params) as res:
            if res.status == 429:  # Rate-limited
                await asyncio.sleep(1)
                if retry > 0:
                    return await self._get(endpoint, params, retry - 1)
                raise RuntimeError("Twitch rate limit exceeded")

            if res.status == 401:  # Token expired
                await self.fetch_token()
                headers["Authorization"] = f"Bearer {self.token}"
                async with self.session.get(HELIX_URL + endpoint, headers=headers, params=params) as res2:
                    return await res2.json()

            return await res.json()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
