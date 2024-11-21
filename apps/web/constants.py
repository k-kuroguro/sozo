import os
from typing import Final

APP_ROOT: Final[str] = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR: Final[str] = os.path.join(APP_ROOT, "static")
TEMPLATES_DIR: Final[str] = os.path.join(APP_ROOT, "templates")
