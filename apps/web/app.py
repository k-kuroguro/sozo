import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from libs.ipc import BaseSubscriber
from libs.schemas.monitor_msg import ConcentrationStatus, MonitorMsg

from .aggregator import PeriodicAggregator
from .constants import STATIC_DIR
from .database import create_db_and_tables, get_session_context
from .router import router
from .store import AccumalatedScoreStore, IncomingDataStore, ParameterStore


class App:
    def __init__(
        self, subscriber: BaseSubscriber[MonitorMsg], *, evolution_threshold: float = 5000
    ):
        self._subscriber = subscriber
        self._incoming_data_store = IncomingDataStore()
        self._accumalated_score_store = AccumalatedScoreStore()
        self._aggregator = PeriodicAggregator(
            store=self._incoming_data_store, session_context_getter=get_session_context
        )

        self._parameter_store = ParameterStore()
        self._parameter_store.evolution_threshold = evolution_threshold

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
        self._incoming_data_store.latest_monitor_msg = msg
        if isinstance(msg.payload, ConcentrationStatus):
            self._accumalated_score_store.add(msg.payload.overall_score)
            if (
                self._accumalated_score_store.accumalated_score
                > self._parameter_store.evolution_threshold
            ):
                self._parameter_store.is_evolved = True
