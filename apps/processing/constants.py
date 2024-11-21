import os
from typing import Final

APP_ROOT: Final[str] = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR: Final[str] = os.path.join(APP_ROOT, "models")

LANDMARKS_NUM: Final[int] = 68
