from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


@dataclass(slots=True, frozen=True)
class ConcentrationStatus:
    """Represent the mearured concentration score

    Args:
        overall_score (float): Overall concentration score, where a higher value indicates better concentration.
        sleeping_confidence (float): Confidence score of the sleeping state, ranging from [0,1], where a higher value indicates a higher probability of being asleep.
    """

    overall_score: float
    sleeping_confidence: float


@dataclass(slots=True, frozen=True)
class MonitorError:
    """Represent an error in measurement.

    Args:
        type (Type): Type of the error.
        msg (str): Error message.
    """

    class Type(int, Enum):
        """Enumerate types of errors in measurement."""

        UNKNOWN = auto()
        """Unknown error."""

    type: Type
    msg: str


Payload = ConcentrationStatus | MonitorError


@dataclass(slots=True, frozen=True)
class MonitorMsg:
    """Represent a monitoring result or error.

    Args:
        timestamp (datetime): Timestamp indicating when the monitoring result was recorded.
        payload (Payload): Monitoring result or error.
    """

    timestamp: datetime
    payload: Payload
