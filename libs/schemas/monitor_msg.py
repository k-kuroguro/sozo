from dataclasses import dataclass
from datetime import datetime
from enum import Enum, Flag, auto


class PenaltyFactor(Flag):
    """Represent factors that penalize the concentration score."""

    NONE = 0
    """No factor."""

    IS_ABSENT = auto()
    """The person is absent."""

    IS_DROWSY = auto()
    """The person is drowsy."""

    IS_LOOKING_AWAY = auto()
    """The person is looking away."""


@dataclass(slots=True, frozen=True)
class ConcentrationStatus:
    """Represent the mearured concentration score.

    Args:
        overall_score (float): Overall concentration score, where a higher value indicates better concentration. The value is in the range [0, 100].
        penalty_factor (PenaltyFactor): Factors that penalize the concentration score.
    """

    overall_score: float
    penalty_factor: PenaltyFactor = PenaltyFactor.NONE


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
