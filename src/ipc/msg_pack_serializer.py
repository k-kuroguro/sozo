from datetime import datetime

from msgspec.msgpack import Decoder, Encoder

from schema import ConcentrationStatus, MonitorError, MonitorMsg

from .base_serializer import BaseSerializer

# TODO: raise exception


class MsgPackSerializer(BaseSerializer[MonitorMsg]):
    def __init__(self) -> None:
        self._encoder = Encoder()
        self._decoder = Decoder()

    def serialize(self, msg: MonitorMsg) -> bytes:
        return self._encoder.encode(msg)

    def deserialize(self, data: bytes) -> MonitorMsg:
        d = self._decoder.decode(data)

        timestamp = datetime.fromisoformat(d["timestamp"])
        payload: ConcentrationStatus | MonitorError
        if "overall_score" in d["payload"]:
            payload = ConcentrationStatus(
                overall_score=d["payload"]["overall_score"],
                sleeping_confidence=d["payload"]["sleeping_confidence"],
            )
        else:
            payload = MonitorError(
                type=MonitorError.Type(d["payload"]["type"]),
                msg=d["payload"]["msg"],
            )

        return MonitorMsg(timestamp=timestamp, payload=payload)
