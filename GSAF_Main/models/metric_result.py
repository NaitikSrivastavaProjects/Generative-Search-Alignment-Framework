from dataclasses import dataclass, field


@dataclass
class MetricResult:
    factor: str
    score: int = None
    status: str = None
    details: dict = field(default_factory=dict)
    recommendations: list = field(default_factory=list)
    error: str = None

    def to_dict(self):
        return {
            "factor": self.factor,
            "score": self.score,
            "status": self.status,
            "details": self.details,
            "recommendations": self.recommendations,
            "error": self.error
        }