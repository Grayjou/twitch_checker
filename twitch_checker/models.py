"""
Models and data structures used by twitch_checker.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional


StatusChange = Literal["UP", "DOWN"]


class StreamerStatusChange(str, Enum):
    """Enum representing live/offline transitions."""
    UP = "UP"
    DOWN = "DOWN"


@dataclass(frozen=True)
class StreamerStatus:
    """Represents the current and recent live status of a Twitch streamer."""
    login: str
    is_live: bool
    change: Optional[StatusChange]
    data: dict

    def __repr__(self):
        return (
            f"StreamerStatus(login={self.login!r}, "
            f"is_live={self.is_live}, change={self.change!r})"
        )

    def __str__(self):
        status = "LIVE" if self.is_live else "offline"
        change_info = f", change={self.change}" if self.change else ""
        return f"{self.login} is {status}{change_info}"

    def __hash__(self):
        return hash((self.login, self.is_live, self.change))

    def __eq__(self, other):
        if not isinstance(other, StreamerStatus):
            return NotImplemented
        return (
            self.login == other.login
            and self.is_live == other.is_live
            and self.change == other.change
            and self.data == other.data
        )
