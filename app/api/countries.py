from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.country import country_crud
from app.schemas.country import CountryResponse, ErrorResponse
from app.services.external_api import external_api_service
from app.services.image_service import image_service

router = APIRouter(prefix="/countries", tags=["countries"])


@router.post(
    "/refresh",
    status_code=200,
    responses={
        200: {"description": "Countries refreshed successfully"},
        503: {
            "model": ErrorResponse,
            "description": "External data source unavailable",
        },
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def refresh_countries(db: AsyncSession = Depends(get_db)):
    """
    Fetch all countries and exchange rates, then cache them in the database.
    Also generates a summary image.
    """
    try:
        # Fetch data from external APIs
        countries_data = await external_api_service.fetch_countries()
        exchange_rates = await external_api_service.fetch_exchange_rates()

        # Process and store/update countries
        created_count = 0
        updated_count = 0

        for country_raw in countries_data:
            try:
                # Process country data
                country_data = await external_api_service.process_country_data(
                    country_raw, exchange_rates
                )

                # Skip if name is missing
                if not country_data.get("name"):
                    continue

                # Upsert country
                _, is_new = await country_crud.upsert(db, country_data)

                if is_new:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                # Log error but continue processing other countries
                print(f"Error processing country: {str(e)}")
                continue

        # Commit all changes
        await db.commit()

        # Generate summary image
        total_countries = await country_crud.get_count(db)
        top_countries_data = await country_crud.get_top_by_gdp(db, limit=5)
        last_refreshed = await country_crud.get_last_refreshed(db)

        top_countries = [
            (
                country.name,
                float(country.estimated_gdp) if country.estimated_gdp else None,
            )
            for country in top_countries_data
        ]

        if last_refreshed:
            image_service.generate_summary_image(
                total_countries, top_countries, last_refreshed
            )

        return {
            "message": "Countries refreshed successfully",
            "total_countries": total_countries,
            "created": created_count,
            "updated": updated_count,
            "last_refreshed_at": last_refreshed,
        }

    except Exception as e:
        error_message = str(e)
        if "Could not fetch data from" in error_message:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "External data source unavailable",
                    "details": error_message,
                },
            )
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": error_message},
        )


@router.get(
    "",
    response_model=List[CountryResponse],
    responses={
        200: {"description": "List of countries"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_countries(
    region: Optional[str] = Query(None, description="Filter by region (e.g., Africa)"),
    currency: Optional[str] = Query(
        None, description="Filter by currency code (e.g., NGN)"
    ),
    sort: Optional[str] = Query(
        None,
        description="Sort order: gdp_desc, gdp_asc, name_asc, name_desc, population_desc, population_asc",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all countries from the database with optional filters and sorting.
    """
    try:
        countries = await country_crud.get_all(
            db, region=region, currency=currency, sort=sort
        )
        return countries
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        )


@router.get(
    "/{name}",
    response_model=CountryResponse,
    responses={
        200: {"description": "Country details"},
        404: {"model": ErrorResponse, "description": "Country not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_country(name: str, db: AsyncSession = Depends(get_db)):
    """
    Get a single country by name (case-insensitive).
    """
    try:
        country = await country_crud.get_by_name(db, name)
        if not country:
            raise HTTPException(status_code=404, detail={"error": "Country not found"})
        return country
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        )


@router.delete(
    "/{name}",
    status_code=200,
    responses={
        200: {"description": "Country deleted successfully"},
        404: {"model": ErrorResponse, "description": "Country not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_country(name: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a country record by name.
    """
    try:
        country = await country_crud.get_by_name(db, name)
        if not country:
            raise HTTPException(status_code=404, detail={"error": "Country not found"})

        await country_crud.delete(db, country)
        await db.commit()

        return {"message": f"Country '{name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        )
