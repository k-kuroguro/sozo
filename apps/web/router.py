from dataclasses import fields
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from libs.schemas.monitor_msg import ConcentrationStatus, MonitorError

from .constants import TEMPLATES_DIR
from .database import get_session_generator
from .schemas import AggregatedConcentrationStatus
from .store import AccumalatedScoreStore, IncomingDataStore, ParameterStore

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

IncomingDataStoreDep = Annotated[IncomingDataStore, Depends(IncomingDataStore)]
ParameterStoreDep = Annotated[ParameterStore, Depends(ParameterStore)]


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, store: ParameterStoreDep) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "evolution_threshold": store.evolution_threshold,
            "is_evolved": 1 if store.is_evolved else 0,
        },
    )


class EventType(str, Enum):
    STATUS = "status_msg"
    ERROR = "error_msg"

    @classmethod
    def from_status_or_error(
        cls, status_or_error: ConcentrationStatus | MonitorError
    ) -> "EventType":
        if isinstance(status_or_error, ConcentrationStatus):
            return cls.STATUS
        return cls.ERROR

    def __str__(self) -> str:
        return self.value


def to_json(status_or_error: ConcentrationStatus | MonitorError) -> dict:
    if isinstance(status_or_error, ConcentrationStatus):
        return {
            "overall_score": status_or_error.overall_score,
            "penalty_factor": status_or_error.penalty_factor.get_active_factor_names(),
            "accumulated_score": AccumalatedScoreStore().accumalated_score,
        }
    return {"type": status_or_error.type.name, "msg": status_or_error.msg}


def to_sse_msg(status_or_error: ConcentrationStatus | MonitorError) -> str:
    event = EventType.from_status_or_error(status_or_error)
    data = to_json(status_or_error)
    return f"event: {event}\ndata: {data}\n\n"


@router.get("/monitor")
def monitor(
    store: IncomingDataStoreDep,
) -> StreamingResponse:
    def generator(store: IncomingDataStoreDep):
        if store.latest_monitor_msg:
            yield to_sse_msg(store.latest_monitor_msg.payload)
        while True:
            store.wait_for_change()
            if store.latest_monitor_msg:
                yield to_sse_msg(store.latest_monitor_msg.payload)

    return StreamingResponse(
        generator(store),
        media_type="text/event-stream",
        headers={"Connection": "keep-alive", "Cache-Control": "no-cache"},
    )


@router.get("/status/by-date", response_model=Sequence[AggregatedConcentrationStatus])
def get_status_by_date(
    target_date: date, session: Annotated[Session, Depends(get_session_generator)]
) -> Sequence[AggregatedConcentrationStatus]:
    statement = select(AggregatedConcentrationStatus).where(
        AggregatedConcentrationStatus.start_time >= target_date,
        AggregatedConcentrationStatus.end_time <= target_date + timedelta(days=1),
    )
    return session.exec(statement).all()


@router.get("/status/by-hour", response_model=Sequence[AggregatedConcentrationStatus])
def get_status_by_hour(
    target_hour: datetime, session: Annotated[Session, Depends(get_session_generator)]
) -> Sequence[AggregatedConcentrationStatus]:
    target_hour = target_hour.replace(minute=0, second=0, microsecond=0)
    statement = select(AggregatedConcentrationStatus).where(
        AggregatedConcentrationStatus.start_time >= target_hour,
        AggregatedConcentrationStatus.end_time <= target_hour + timedelta(hours=1),
    )
    return session.exec(statement).all()
