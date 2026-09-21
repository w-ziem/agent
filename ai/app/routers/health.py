from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    # celowo bez sprawdzania zależności zewnętrznych (contract.md)
    return {"status": "ok"}
