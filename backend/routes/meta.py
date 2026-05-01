from fastapi import APIRouter

from core.config import SUPPORTED_DATASETS
from schemas.request_response import DatasetsResponse

router = APIRouter()


@router.get("/datasets", response_model=DatasetsResponse)
def list_datasets() -> DatasetsResponse:
    return DatasetsResponse(datasets=SUPPORTED_DATASETS)
