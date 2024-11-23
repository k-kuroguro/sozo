from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class HeadDirection:
    """Represent a normalized 2D head direction.

    Attributes:
        x (float): The x component of the direction.
        y (float): The y component of the direction.
    """

    x: float
    y: float


@dataclass(slots=True, frozen=True)
class AnalysisMsg:
    """Represent an analysis result.

    Attributes:
        head_direction (HeadDirection): The detected head direction.
    """

    head_direction: HeadDirection
