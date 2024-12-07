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
        timestamp (datetime): Timestamp indicating when the analysis result was recorded.
        is_absent (bool): Indicates whether the face is absent in the frame
        head_direction (HeadDirection | None): The detected head direction. If the face is absent, this field is None.
    """

    timestamp: datetime
    is_absent: bool
    head_direction: HeadDirection | None
