from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class AnswerFilters(BaseModel):
    subject: str | None = None
    doc_type: str | None = None
    year: int | None = None


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    filters: AnswerFilters = AnswerFilters()
    top_k: int = Field(default=8, ge=1, le=50)


class Source(BaseModel):
    document_id: str
    path: str
    page: int | None
    snippet: str
    score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post("/answer")
def answer(request: AnswerRequest) -> AnswerResponse:
    # shortcut: stub bez LLM i retrievalu, podmienić w 0.10 (LLM) i 1.13 (kontekst)
    return AnswerResponse(
        answer=f"Nie mam jeszcze podłączonego modelu. Pytanie: {request.question}",
        sources=[],
    )
