from typing import Final, NamedTuple

import numpy as np
import numpy.typing as npt

from libs.schemas.analysis_msg import HeadDirection

from .constants import LANDMARKS_NUM


class Face(NamedTuple):
    """Represents a detected face.

    Attributes:
        x (int): The x-coordinate of the top-left corner of the bbox.
        y (int): The y-coordinate of the top-left corner of the bbox.
        w (int): The width of the bbox.
        h (int): The height of the bbox.
        confidence (float): The confidence score of the detection.
    """

    x: int
    y: int
    w: int
    h: int
    confidence: float

    @property
    def area(self) -> int:
        """Calculates the area of the bbox.

        Returns:
            int: The area of the bbox.
        """
        return self.w * self.h


class HeadPose(NamedTuple):
    """Represents the 3d head pose.

    Attributes:
        yaw (float): The yaw angle in degrees, representing left-right rotation.
        pitch (float): The pitch angle in degrees, representing up-down tilt.
        roll (float): The roll angle in degrees, representing side tilt.
    """

    yaw: float
    pitch: float
    roll: float

    def to_direction(self) -> HeadDirection:
        """Converts to the 2D head direction.

        Returns:
            HeadDirection: The 2D head direction.
        """
        x, y = np.sin(np.radians(self.yaw)), -np.sin(np.radians(self.pitch))
        norm = np.linalg.norm((x, y))
        return HeadDirection(float(x / norm), float(y / norm))


class FacialLandmarks2d(np.ndarray):
    """A fixed-shape np.ndarray representing 2D facial landmarks.

    The landmarks are stored as a np.ndarray of shape `(LANDMARKS_NUM, 2)`,
    where each row corresponds to a (x, y) coordinate of a landmark.
    """

    _EXPECTED_SHAPE: Final = (LANDMARKS_NUM, 2)

    def __new__(cls, input_array: npt.ArrayLike) -> "FacialLandmarks2d":
        """
        Args:
            input_array (npt.ArrayLike): Input data that can be converted array of shape `(LANDMARKS_NUM, 2)`.

        Raises:
            ValueError: If the input data does not have the expected shape.
        """
        obj = np.asarray(input_array, dtype=np.int16).view(cls)

        if obj.shape != cls._EXPECTED_SHAPE:
            raise ValueError(f"Expected shape {cls._EXPECTED_SHAPE}, got {obj.shape}")

        return obj


class FacialLandmarks3d(np.ndarray):
    """A fixed-shape np.ndarray representing 3D facial landmarks.

    The landmarks are stored as a np.ndarray of shape `(LANDMARKS_NUM, 3)`,
    where each row corresponds to a (x, y, z) coordinate of a landmark.
    """

    _EXPECTED_SHAPE: Final = (LANDMARKS_NUM, 3)

    def __new__(cls, input_array: npt.ArrayLike) -> "FacialLandmarks3d":
        """
        Args:
            input_array (npt.ArrayLike): Input data that can be converted array of shape `(LANDMARKS_NUM, 3)`.

        Raises:
            ValueError: If the input data does not have the expected shape.
        """
        obj = np.asarray(input_array, dtype=np.int16).view(cls)

        if obj.shape != cls._EXPECTED_SHAPE:
            raise ValueError(f"Expected shape {cls._EXPECTED_SHAPE}, got {obj.shape}")

        return obj
