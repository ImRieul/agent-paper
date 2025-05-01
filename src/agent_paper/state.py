from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TypeVar, Generic


T = TypeVar('T', bound='OutlineSection')


class OutlineSection(BaseModel):
    id: str
    title: str
    why: str
    how: Optional[str] = None
    data: Optional[str] = None
    subsections: List[T] = Field(default_factory=list)
    content: Optional[str] = None


class OutlineReview(BaseModel):
    topic_alignment: str
    structure_coherence: str
    completeness: str


class OutlineStructure(BaseModel):
    title: str = ""
    sections: List[OutlineSection] = Field(default_factory=list)
    review: Optional[OutlineReview] = None


class AgentPaperState(BaseModel):
    outline: Optional[OutlineStructure] = None
    id: Optional[str] = None  # CrewAI Flow에서 자동으로 할당하는 ID 필드


# 타입 힌트를 위한 순환 참조 해결
OutlineSection.update_forward_refs()
