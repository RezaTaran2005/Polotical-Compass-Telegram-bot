

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class UserSession:
    current_index: int = 0
    answers: dict[int, str] = field(default_factory=dict)
    active_message_id: int | None = None


# Global registry: user_id → UserSession
_sessions: dict[int, UserSession] = {}


def get_session(user_id: int) -> UserSession | None:
    return _sessions.get(user_id)


def create_session(user_id: int) -> UserSession:
    session = UserSession()
    _sessions[user_id] = session
    return session


def delete_session(user_id: int) -> None:
    _sessions.pop(user_id, None)
