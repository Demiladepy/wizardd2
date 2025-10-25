from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.crud import country as country_crud
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter()

@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    """Get API status"""
    stats = await country_crud.get_stats(db)
    return {
        "total_countries": stats["total_countries"],
        "last_refreshed_at": stats["last_refreshed_at"].isoformat() + "Z" if stats["last_refreshed_at"] else None
    }

@router.get("/countries/image")
async def get_summary_image():
    """Serve the generated summary image"""
    # Use absolute path from project root
    image_path = Path("cache/summary.png")
    
    # Check if file exists
    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )
    
    # Return the actual PNG file
    return FileResponse(
        path=str(image_path.absolute()),
        media_type="image/png",
        filename="summary.png"
    )
