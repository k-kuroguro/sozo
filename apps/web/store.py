from threading import Event, Lock

from libs.schemas.monitor_msg import MonitorMsg


class IncomingDataStore:
    """Singleton class to store data received via IPC."""

    _instance: "IncomingDataStore | None" = None
    _lock = Lock()

    def __new__(cls) -> "IncomingDataStore":
        if cls._instance is None:
            with cls._lock:
                cls._instance = super(IncomingDataStore, cls).__new__(cls)
                cls._instance._initialized = False  # type: ignore
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:  # type: ignore
            return
        self._initialized = True
        self._latest_monitor_msg: MonitorMsg | None = None
        self._changed_event = Event()

    def wait_for_change(self, timeout: float | None = None) -> bool:
        """Wait for the data to change.

        Args:
            timeout (float | None, optional): The maximum time (in seconds) to wait for the event. If `None`, waits indefinitely.

        Returns:
            bool: `True` if the event was set within the timeout period, `False` if the timeout was reached.
        """
        return self._changed_event.wait(timeout)

    @property
    def latest_monitor_msg(self) -> MonitorMsg | None:
        return self._latest_monitor_msg

    @latest_monitor_msg.setter
    def latest_monitor_msg(self, value: MonitorMsg | None) -> None:
        self._latest_monitor_msg = value
        self._changed_event.set()
        self._changed_event.clear()


class AccumalatedScoreStore:
    """Singleton class to store accumalated score."""

    _instance: "AccumalatedScoreStore | None" = None
    _lock = Lock()

    def __new__(cls) -> "AccumalatedScoreStore":
        if cls._instance is None:
            with cls._lock:
                cls._instance = super(AccumalatedScoreStore, cls).__new__(cls)
                cls._instance._initialized = False  # type: ignore
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:  # type: ignore
            return
        self._initialized = True
        self._accumalated_score: float = 0

    def add(self, score: float) -> None:
        self._accumalated_score += score

    @property
    def accumalated_score(self) -> float:
        return self._accumalated_score


class ParameterStore:
    """Singleton class to store parameters."""

    _instance: "ParameterStore | None" = None
    _lock = Lock()

    def __new__(cls) -> "ParameterStore":
        if cls._instance is None:
            with cls._lock:
                cls._instance = super(ParameterStore, cls).__new__(cls)
                cls._instance._initialized = False  # type: ignore
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:  # type: ignore
            return
        self._initialized = True
        self._evolution_threshold: float = 0.0
        self._is_evolved = False

    @property
    def evolution_threshold(self) -> float | None:
        return self._evolution_threshold

    @evolution_threshold.setter
    def evolution_threshold(self, value: float) -> None:
        self._evolution_threshold = value

    @property
    def is_evolved(self) -> bool:
        return self._is_evolved

    @is_evolved.setter
    def is_evolved(self, value: bool) -> None:
        self._is_evolved = value
