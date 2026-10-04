from app.ingest.normalize import Transfer
from app.patterns.dormancy_burst import DormancyBurstDetector
from app.patterns.fan_in import FanInDetector
from app.patterns.fan_out import FanOutDetector
from app.patterns.peel_chain import PeelChainDetector
from app.patterns.rapid_forwarding import RapidForwardingDetector
from app.patterns.round_trip import RoundTripDetector
from app.patterns.structuring import StructuringDetector


class PatternRegistry:
    def __init__(self):
        self.detectors = [
            FanOutDetector(),
            FanInDetector(),
            RapidForwardingDetector(),
            PeelChainDetector(),
            DormancyBurstDetector(),
            StructuringDetector(),
            RoundTripDetector()
        ]

    def detect_all(self, transfers: list[Transfer]) -> list[dict]:
        results = []
        for d in self.detectors:
            results.extend(d.detect(transfers))
        return results
