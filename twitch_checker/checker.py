"""
High-level Twitch stream checker with state tracking and change detection.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Iterable, Optional, Set

from twitch_checker.api import TwitchAPI
from twitch_checker.models import StreamerStatus, StatusChange
from twitch_checker.utils import chunked


EXPORT_VERSION = 1


class TwitchChecker:
    """
    Tracks Twitch user existence, live state, and state transitions.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        logins: Optional[Iterable[str]] = None,
        *,
        cooldown_seconds: int = 0,
        checked_existence: Optional[Iterable[str]] = None,
    ):
        self.api = TwitchAPI(client_id, client_secret)

        self._logins: Set[str] = set()
        self.was_online: Dict[str, bool] = {}
        self.checked_existence: Set[str] = set(checked_existence or [])
        self.to_check_existence: Set[str] = set()
        self.cooldown_seconds = cooldown_seconds
        self.last_time_offline: Dict[str, datetime] = {}
        self.user_ids: Dict[str, str] = {}
        if logins:
            self.logins = logins

    # -------------------- Login Management --------------------

    @property
    def logins(self) -> Set[str]:
        return self._logins

    @logins.setter
    def logins(self, items: Iterable[str]) -> None:
        normalized = {
            login.lower().strip()
            for login in items
            if isinstance(login, str) and login.strip()
        }
        self._logins = normalized
        self.to_check_existence = normalized - self.checked_existence

    # -------------------- Existence Check --------------------

    async def _batch_check_existence(self) -> None:
        new = self.to_check_existence
        if not new:
            return

        exists = await self.batch_user_exists(new)

        for login in new:
            self.checked_existence.add(login)
            if login not in exists:
                if login in self._logins:
                    self._logins.remove(login)

        self.to_check_existence.clear()

    async def batch_user_exists(self, logins: Set[str]) -> Set[str]:
        existing = set()
        for chunk in chunked(logins):
            params = [("login", login) for login in chunk]
            data = await self.api._get("users", params)
            for user in data.get("data", []):
                login_lower = user["login"].lower()
                existing.add(login_lower)
                self.user_ids[login_lower] = user["id"]  # Cache the ID
        return existing

    # -------------------- Live Status --------------------

    async def batch_is_live(self, logins: Set[str]) -> Dict[str, dict]:
        live_map = {}
        for chunk in chunked(logins):
            params = [("user_login", login) for login in chunk]
            data = await self.api._get("streams", params)
            for stream in data.get("data", []):
                live_map[stream["user_login"].lower()] = stream
        return live_map

    async def check_streamer_status(self, login: str, live_data: dict) -> StreamerStatus:
        now = datetime.utcnow()
        is_live = live_data is not None
        was_live = self.was_online.get(login, False)

        if is_live:
            self.last_time_offline.pop(login, None)
            change: Optional[StatusChange] = "UP" if not was_live else None
            self.was_online[login] = True
            return StreamerStatus(login, True, change, live_data)

        if was_live:
            first_offline = self.last_time_offline.get(login)
            if first_offline is None:
                self.last_time_offline[login] = now
                return StreamerStatus(login, True, None, live_data or {})

            if (now - first_offline).total_seconds() < self.cooldown_seconds:
                return StreamerStatus(login, True, None, live_data or {})

            self.was_online[login] = False
            return StreamerStatus(login, False, "DOWN", live_data or {})

        self.was_online[login] = False
        return StreamerStatus(login, False, None, live_data or {})

    # -------------------- Public API --------------------

    async def check_logins(self) -> Set[StreamerStatus]:
        await self._batch_check_existence()
        live_map = await self.batch_is_live(self._logins)

        result = {
            await self.check_streamer_status(login, live_map.get(login))
            for login in self._logins
        }
        return result

    async def classify_logins(self, logins: Iterable[str]) -> Dict[str, str]:
        normalized = {l.lower().strip() for l in logins if l.strip()}
        exists = await self.batch_user_exists(normalized)

        nonexistent = normalized - exists
        live_map = await self.batch_is_live(exists)
        live = set(live_map.keys())
        not_live = exists - live

        return {
            **{login: "does_not_exist" for login in nonexistent},
            **{login: "exists_and_live" for login in live},
            **{login: "exists_but_not_live" for login in not_live},
        }

    # -------------------- Serialization --------------------

    def to_dict(self) -> dict:
        return {
            "version": EXPORT_VERSION,
            "logins": sorted(self._logins),
            "checked_existence": sorted(self.checked_existence),
            "was_online": dict(self.was_online),
            "last_time_offline": {
                login: ts.isoformat() for login, ts in self.last_time_offline.items()
            },
            "cooldown_seconds": self.cooldown_seconds,
        }

    def update_from_dict(self, data: dict) -> None:
        if data.get("version", 0) != EXPORT_VERSION:
            raise ValueError("Unsupported export version")

        self._logins = set(data["logins"])
        self.checked_existence = set(data["checked_existence"])
        self.was_online = data.get("was_online", {})

        self.last_time_offline = {
            login: datetime.fromisoformat(ts)
            for login, ts in data.get("last_time_offline", {}).items()
        }

        self.cooldown_seconds = int(data["cooldown_seconds"])

    def export_json(self, path: Optional[str] = None) -> str:
        json_str = json.dumps(self.to_dict(), indent=4)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str

    @classmethod
    def from_dict(cls, state: dict, *, client_id: str, client_secret: str):
        obj = cls(client_id=client_id, client_secret=client_secret)
        obj.update_from_dict(state)
        return obj

    @classmethod
    def from_json(cls, path: str, *, client_id: str, client_secret: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, client_id=client_id, client_secret=client_secret)

    # -------------------- Shutdown --------------------

    async def close(self):
        await self.api.close()

    def __del__(self):
        asyncio.create_task(self.close())


    def get_user_id(self, login: str) -> Optional[str]:
        """Get cached user ID for a login (must check existence first)."""
        return self.user_ids.get(login.lower())