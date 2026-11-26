
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.analysis.analysis_service import AnalysisService

router = APIRouter()

logger = logging.getLogger(__name__)


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.get("/analyze/{groww_symbol}")
async def analyze_stock(
    groww_symbol: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    try:
        result = await analysis_service.analyze_stock(
            groww_symbol.upper()
        )

        return result

    except ValueError as exc:
        logger.exception("Analysis validation error")

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected stock analysis error")

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc
