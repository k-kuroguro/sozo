import cv2

from libs.types import MatLike

from .schemas import Face


class FaceDetector:
    """Face detector using OpenCV DNN module."""

    def __init__(
        self,
        model_path: str,
        config_path: str,
        *,
        confidence_threshold: float = 0.6,
    ) -> None:
        """
        Args:
            model_path (str): The path to the pre-trained model file.
            config_path (str): The path to the network configuration file.
            confidence_threshold (float, optional): The minimum confidence score for a detection to be considered valid.
        """
        self._net = cv2.dnn.readNet(model_path, config_path)
        self._confidence_threshold = confidence_threshold

    def detect(self, image: MatLike) -> list[Face]:
        """Detect faces in the provided image.

        The image is resized before being passed into the DNN.
        Detected faces with a confidence score greater than the specified threshold are returned.

        Args:
            image (MatLike): The OpenCV image.

        Returns:
            list[Face]: A list of detected faces.
        """
        height, width = image.shape[:2]

        inputBlob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0), True, False
        )
        self._net.setInput(inputBlob)
        detections = self._net.forward()

        faces: list[Face] = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self._confidence_threshold:
                box = detections[0, 0, i, 3:7] * [width, height, width, height]
                (x, y, x2, y2) = box.astype("int")
                faces.append(Face(x, y, x2 - x, y2 - y, confidence))

        return faces
