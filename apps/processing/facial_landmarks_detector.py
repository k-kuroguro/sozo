import dlib
from imutils import face_utils

from libs.types import MatLike

from .schemas import Face, FacialLandmarks2d


class FacialLandmarksDetector:
    """Facial landmarks detector using dlib.shape_predictor."""

    def __init__(self, model_path: str) -> None:
        """
        Args:
            model_path (str): The path to the dlib.shape_predictor model file.
        """
        self._detector = dlib.shape_predictor(model_path)

    def detect(self, gray_image: MatLike, face: Face) -> FacialLandmarks2d:
        """
        Detects facial landmarks from the given grayscale image and face.

        Args:
            gray_image (MatLike): The grayscale OpenCV image.
            face (Face): The face to detect landmarks.

        Returns:
            FacialLandmarks2d: The detected facial landmarks.
        """
        x, y, w, h, _ = face
        landmarks = self._detector(gray_image,  dlib.rectangle(x, y, x + w, y + h))
        return FacialLandmarks2d(face_utils.shape_to_np(landmarks))
