from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RoutineBlock(BaseModel):
    morning: List[str] = Field(default_factory=list)
    evening: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    id: str
    age_band: str
    skin_type: str
    concerns: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    routine: RoutineBlock = Field(default_factory=RoutineBlock)
    ingredients: List[str] = Field(default_factory=list)
    product_classes: List[str] = Field(default_factory=list)
    warning: Optional[str] = None
    image_url: Optional[str] = None

