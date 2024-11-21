from typing import Callable, TypeVar

import cv2

T = TypeVar("T")

MatLike = cv2.typing.MatLike
Callback = Callable[[T], None]
