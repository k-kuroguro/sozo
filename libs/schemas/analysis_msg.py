from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class HeadDirection:
    """Represents the direction of the head in terms of horizontal and vertical angles in degrees.

    Attributes:
        x (float): Horizontal angle (deg) of the head, where positive values indicate rightward rotation.
        y (float): Vertical angle (deg) of the head, where positive values indicate upward tilt.
    """

    x: float
    y: float


@dataclass(slots=True, frozen=True)
class AnalysisMsg:
    """Represent an analysis result.

    Attributes:
        head_direction (HeadDirection): The detected head direction.
    """

    timestamp: datetime
    head_direction: HeadDirection
