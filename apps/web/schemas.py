from datetime import datetime

from sqlmodel import Field, SQLModel


class AggregatedConcentrationStatus(SQLModel, table=True):
    __tablename__ = "aggregated_concentration_status"

    id: int | None = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: datetime
    overall_score: float
    sleeping_confidence: float