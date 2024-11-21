from msgspec.msgpack import Decoder, Encoder

from libs.schemas.analysis_msg import AnalysisMsg

from .base_serializer import BaseSerializer

# TODO: raise exception


class AnalysisMsgSerializer(BaseSerializer[AnalysisMsg]):
    def __init__(self) -> None:
        self._encoder = Encoder()
        self._decoder = Decoder(AnalysisMsg)

    def serialize(self, obj: AnalysisMsg) -> bytes:
        return self._encoder.encode(obj)

    def deserialize(self, data: bytes) -> AnalysisMsg:
        return self._decoder.decode(data)
