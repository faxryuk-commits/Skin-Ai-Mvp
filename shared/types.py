from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Routine:
    morning: List[str] = field(default_factory=list)
    evening: List[str] = field(default_factory=list)


@dataclass
class AnalysisPayload:
    id: str
    age_band: str
    skin_type: str
    concerns: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    routine: Routine = field(default_factory=Routine)
    ingredients: List[str] = field(default_factory=list)
    product_classes: List[str] = field(default_factory=list)
    warning: Optional[str] = None

