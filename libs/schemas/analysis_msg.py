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
class BothEyeAspectRatio:
    """Represents the eye aspect ratio (EAR) of both eyes.

    Attributes:
        left (float): EAR of the left eye.
        right (float): EAR of the right eye.
    """

    left: float
    right: float


@dataclass(slots=True, frozen=True)
class AnalysisMsg:
    """Represent an analysis result.

    Attributes:
        timestamp (datetime): Timestamp indicating when the analysis result was recorded.
        is_absent (bool): Indicates whether the face is absent in the frame
        both_eye_aspect_ratio (BothEyeAspectRatio | None): The detected eye aspect ratio of both eyes. If the face is absent, this field is None.
        head_direction (HeadDirection | None): The detected head direction. If the face is absent, this field is None.
    """

    timestamp: datetime
    is_absent: bool
    both_eye_aspect_ratio: BothEyeAspectRatio | None
    head_direction: HeadDirection | None
