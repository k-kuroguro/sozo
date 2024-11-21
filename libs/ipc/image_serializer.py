from typing import Final

import cv2
import numpy as np

from libs.types import MatLike

from .base_serializer import BaseSerializer

# TODO: raise exception from ret_code


class ImageSerializer(BaseSerializer[MatLike]):
    ext: Final[str] = ".jpg"

    def __init__(self, jpg_quality: int = 95) -> None:
        self._jpg_quality = jpg_quality

    def serialize(self, obj: MatLike) -> bytes:
        _, buf = cv2.imencode(self.ext, obj, [int(cv2.IMWRITE_JPEG_QUALITY), self._jpg_quality])
        return buf.tobytes()

    def deserialize(self, data: bytes) -> MatLike:
        return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
