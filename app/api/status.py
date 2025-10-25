from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.country import country_crud
from app.schemas.country import CountryStatusResponse, ErrorResponse
from app.services.image_service import image_service

router = APIRouter(tags=["status"])


@router.get(
    "/status",
    response_model=CountryStatusResponse,
    responses={
        200: {"description": "API status"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_status(db: AsyncSession = Depends(get_db)):
    """
    Get API status showing total countries and last refresh timestamp.
    """
    try:
        total_countries = await country_crud.get_count(db)
        last_refreshed = await country_crud.get_last_refreshed(db)

        return {
            "total_countries": total_countries,
            "last_refreshed_at": last_refreshed,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        )


@router.get(
    "/countries/image",
    responses={
        200: {"description": "Summary image", "content": {"image/png": {}}},
        404: {"model": ErrorResponse, "description": "Summary image not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_summary_image():
    """
    Serve the generated summary image.
    """
    try:
        if not image_service.image_exists():
            raise HTTPException(
                status_code=404, detail={"error": "Summary image not found"}
            )

        image_path = image_service.get_image_path()
        return FileResponse(
            image_path,
            media_type="image/png",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        )
