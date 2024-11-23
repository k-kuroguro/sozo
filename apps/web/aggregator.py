from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import islice
from threading import Thread
from typing import Callable, ContextManager, Deque, Sequence

from sqlmodel import Session

from libs.schemas.monitor_msg import ConcentrationStatus

from .schemas import AggregatedConcentrationStatus
from .store import IncomingDataStore


@dataclass(slots=True, frozen=True)
class TimestampedConcentrationStatus:
    timestamp: datetime
    status: ConcentrationStatus


class PeriodicAggregator:
    """Aggregates concentration status data periodically and saves to DB."""

    _INTERVAL_MINUTES = 5
    _INTERVAL_SECONDS = _INTERVAL_MINUTES * 60

    def __init__(
        self,
        store: IncomingDataStore,
        session_context_getter: Callable[[], ContextManager[Session]],
    ) -> None:
        """
        Args:
            store (IncomingDataStore): Store to get the latest concentration status data.
            session_context_getter (Callable[[], ContextManager[Session]]): Callable that returns a context manager for a session.
        """
        self._store = store
        self._session_context_getter = session_context_getter

        self._is_running = False
        self._thread: Thread | None = None

        now = datetime.now()
        self._last_aggregated_time = now.replace(
            minute=(now.minute // self._INTERVAL_MINUTES) * self._INTERVAL_MINUTES,
            second=0,
            microsecond=0,
        )
        self._buffer: Deque[TimestampedConcentrationStatus] = deque()

    def start(self) -> None:
        """Begins the aggregation process.

        Raises:
            RuntimeError: If the aggregator is already running.
        """

        if self._is_running:
            raise RuntimeError("Aggregator is already running")

        self._is_running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while self._is_running:
            is_timed_out = not self._store.wait_for_change(timeout=self._INTERVAL_SECONDS)
            if self._store.latest_monitor_msg is None or not isinstance(
                self._store.latest_monitor_msg.payload, ConcentrationStatus
            ):
                continue

            if not is_timed_out:
                self._buffer.append(
                    TimestampedConcentrationStatus(
                        timestamp=self._store.latest_monitor_msg.timestamp,
                        status=self._store.latest_monitor_msg.payload,
                    )
                )
            if is_timed_out or self._has_elapsed_interval():
                exclude_latest = not is_timed_out
                end_time = self._last_aggregated_time + timedelta(seconds=self._INTERVAL_SECONDS)

                with self._session_context_getter() as session:
                    target = (
                        list(islice(self._buffer, 0, len(self._buffer) - 1))
                        if exclude_latest
                        else self._buffer
                    )
                    self._aggregate(
                        target,
                        self._last_aggregated_time,
                        end_time,
                        session,
                    )

                self._last_aggregated_time = end_time
                self._clear_buffer(exclude_latest=exclude_latest)

    def _has_elapsed_interval(self) -> bool:
        if not self._buffer:
            return False

        elapsed = self._buffer[-1].timestamp - self._last_aggregated_time
        return elapsed.total_seconds() >= self._INTERVAL_SECONDS

    def _clear_buffer(self, *, exclude_latest: bool = False) -> None:
        if not self._buffer:
            return

        if exclude_latest:
            latest = self._buffer.pop()
            self._buffer.clear()
            self._buffer.append(latest)
        else:
            self._buffer.clear()

    @staticmethod
    def _aggregate(
        data: Sequence[TimestampedConcentrationStatus],
        start_time: datetime,
        end_time: datetime,
        session: Session,
    ) -> None:
        if not data:
            return

        data_len = len(data)
        overall_score = sum(status.status.overall_score for status in data) / data_len
        sleeping_confidence = sum(status.status.sleeping_confidence for status in data) / data_len

        session.add(
            AggregatedConcentrationStatus(
                start_time=start_time,
                end_time=end_time,
                overall_score=overall_score,
                sleeping_confidence=sleeping_confidence,
            )
        )
        session.commit()
