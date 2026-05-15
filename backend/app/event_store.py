"""事件档案的内存与本地 JSON 存储。"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from uuid import uuid4

from app.schemas import EventRecord, EventRecordCreate
from app.scoring import analyze_pressure


_PATH_LOCKS_GUARD = Lock()
_PATH_LOCKS: dict[Path, object] = {}


def get_default_event_store_path() -> Path:
    configured_path = os.getenv("DORM_HARMONY_EVENT_STORE_PATH")
    if configured_path:
        return Path(configured_path)

    return Path(__file__).resolve().parents[1] / ".runtime" / "events.json"


def _get_path_lock(path: Path) -> object:
    lock_key = path.expanduser().resolve()
    with _PATH_LOCKS_GUARD:
        if lock_key not in _PATH_LOCKS:
            _PATH_LOCKS[lock_key] = Lock()
        return _PATH_LOCKS[lock_key]


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: list[EventRecord] = []

    def add(self, payload: EventRecordCreate) -> EventRecord:
        event = EventRecord(
            **payload.model_dump(),
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            single_analysis=analyze_pressure(payload),
        )
        self._events.append(event)
        return event

    def list(self) -> list[EventRecord]:
        return _sort_events(self._events)


class JsonEventStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or get_default_event_store_path()
        self._lock = _get_path_lock(self._path)

    def add(self, payload: EventRecordCreate) -> EventRecord:
        with self._lock:
            events = self._load_events()
            event = EventRecord(
                **payload.model_dump(),
                id=str(uuid4()),
                created_at=datetime.now(timezone.utc),
                single_analysis=analyze_pressure(payload),
            )
            events.append(event)
            self._write_events(events)
            return event

    def list(self) -> list[EventRecord]:
        return _sort_events(self._load_events())

    def _load_events(self) -> list[EventRecord]:
        if not self._path.exists():
            return []

        with self._path.open("r", encoding="utf-8") as file:
            raw_events = json.load(file)

        if not isinstance(raw_events, list):
            raise ValueError("event store JSON must contain a list")

        return [EventRecord.model_validate(event) for event in raw_events]

    def _write_events(self, events: list[EventRecord]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        serialized_events = [
            event.model_dump(mode="json")
            for event in _sort_events(events)
        ]

        temporary_path: str | None = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                delete=False,
                dir=self._path.parent,
                prefix=f".{self._path.name}.",
                suffix=".tmp",
            ) as temporary_file:
                temporary_path = temporary_file.name
                json.dump(
                    serialized_events,
                    temporary_file,
                    ensure_ascii=False,
                    indent=2,
                )
                temporary_file.write("\n")

            os.replace(temporary_path, self._path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                Path(temporary_path).unlink(missing_ok=True)


def _sort_events(events: list[EventRecord]) -> list[EventRecord]:
    return sorted(
        events,
        key=lambda event: (event.event_date, event.created_at),
        reverse=True,
    )
