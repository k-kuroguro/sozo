from dataclasses import fields
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from libs.schemas.monitor_msg import ConcentrationStatus, MonitorError

from .constants import TEMPLATES_DIR
from .store import IncomingDataStore

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

IncomingDataStoreDep = Annotated[IncomingDataStore, Depends(IncomingDataStore)]


@router.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


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


def to_sse_msg(status_or_error: ConcentrationStatus | MonitorError) -> str:
    data = {}
    for field in fields(status_or_error):
        data[field.name] = str(getattr(status_or_error, field.name))
    event = EventType.from_status_or_error(status_or_error)
    return f"event: {event}\ndata: {data}\n\n"


@router.get("/monitor")
async def monitor(
    store: IncomingDataStoreDep,
) -> StreamingResponse:
    async def generator(store: IncomingDataStoreDep):
        if store.latest_monitor_msg:
            yield to_sse_msg(store.latest_monitor_msg.payload)
        while True:
            await store.wait_for_change()
            if store.latest_monitor_msg:
                yield to_sse_msg(store.latest_monitor_msg.payload)

    return StreamingResponse(
        generator(store),
        media_type="text/event-stream",
        headers={"Connection": "keep-alive", "Cache-Control": "no-cache"},
    )
