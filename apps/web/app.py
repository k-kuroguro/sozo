import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from libs.ipc import BaseSubscriber
from libs.schemas.monitor_msg import MonitorMsg

from .aggregator import PeriodicAggregator
from .constants import STATIC_DIR
from .database import create_db_and_tables, get_session_context
from .router import router
from .store import IncomingDataStore


class App:
    def __init__(self, subscriber: BaseSubscriber[MonitorMsg]) -> None:
        self._subscriber = subscriber
        self._aggregator = PeriodicAggregator(
            store=IncomingDataStore(), session_context_getter=get_session_context
        )

        self._fastapi_app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        self._fastapi_app.mount(
            path="/static", app=StaticFiles(directory=STATIC_DIR), name="static"
        )
        self._fastapi_app.include_router(router)

        create_db_and_tables()

    def run(self, host: str, port: int, *, log_level: str | None = None) -> None:
        self._subscriber.start(self._on_message)
        self._aggregator.start()
        uvicorn.run(self._fastapi_app, host=host, port=port, log_level="info")

    def _on_message(self, msg: MonitorMsg) -> None:
        store = IncomingDataStore()
        store.latest_monitor_msg = msg
