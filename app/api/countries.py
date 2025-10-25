from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal
from app.services.external_api import ExternalAPIService
from app.services.image_service import ImageService
from app.crud import country as country_crud
from datetime import datetime
import random
import asyncio

router = APIRouter()

async def generate_image_background():
    """Background task to generate image - creates its own DB session"""
    try:
        # Create new database session for background task
        async with AsyncSessionLocal() as db:
            stats = await country_crud.get_stats(db)
            top_countries = await country_crud.get_top_by_gdp(db, limit=5)
            image_service = ImageService()
            await image_service.generate_summary_image(stats, top_countries)
            print("✅ Image generated successfully")
    except Exception as e:
        print(f"⚠️ Image generation failed: {e}")

@router.post("/countries/refresh")
async def refresh_countries(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Fetch and cache country data"""
    api_service = ExternalAPIService()
    
    try:
        # Fetch data in parallel
        countries_result, rates_result = await asyncio.gather(
            api_service.fetch_countries(),
            api_service.fetch_exchange_rates(),
            return_exceptions=True
        )
        
        # Check for errors
        if isinstance(countries_result, Exception) or countries_result is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "External data source unavailable",
                    "details": "Could not fetch data from restcountries.com"
                }
            )
        
        if isinstance(rates_result, Exception) or rates_result is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "External data source unavailable",
                    "details": "Could not fetch data from open.er-api.com"
                }
            )
        
        countries_data = countries_result
        exchange_rates = rates_result
        
        # Process countries
        processed = []
        for country in countries_data:
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0
            
            # Handle currencies
            if country.get("currencies") and len(country["currencies"]) > 0:
                currency_code = country["currencies"][0].get("code")
                
                if currency_code and currency_code in exchange_rates:
                    exchange_rate = float(exchange_rates[currency_code])
                    random_multiplier = random.uniform(1000, 2000)
                    estimated_gdp = (country["population"] * random_multiplier) / exchange_rate
                elif currency_code:
                    exchange_rate = None
                    estimated_gdp = None
            
            processed.append({
                "name": country["name"],
                "capital": country.get("capital"),
                "region": country.get("region"),
                "population": country["population"],
                "currency_code": currency_code,
                "exchange_rate": exchange_rate,
                "estimated_gdp": estimated_gdp,
                "flag_url": country.get("flag"),
                "last_refreshed_at": datetime.utcnow()
            })
        
        # Upsert to database
        result = await country_crud.upsert_countries_batch(db, processed)
        
        # Schedule image generation in background (don't wait)
        # Note: No db parameter passed - function creates its own session
        background_tasks.add_task(generate_image_background)
        
        # Return immediately
        return {
            "message": "Countries refreshed successfully",
            "total_countries": len(processed),
            "created": result["created"],
            "updated": result["updated"],
            "last_refreshed_at": datetime.utcnow().isoformat() + "Z"
        }
    
    finally:
        await api_service.close()
