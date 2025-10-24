from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CountryBase(BaseModel):
    """Base schema for country"""

    name: str = Field(..., min_length=1, description="Country name")
    capital: Optional[str] = Field(None, description="Capital city")
    region: Optional[str] = Field(None, description="Geographic region")
    population: int = Field(..., ge=0, description="Population count")
    currency_code: Optional[str] = Field(
        None, description="Currency code (e.g., USD, NGN)"
    )
    exchange_rate: Optional[float] = Field(
        None, ge=0, description="Exchange rate to USD"
    )
    estimated_gdp: Optional[float] = Field(None, ge=0, description="Estimated GDP")
    flag_url: Optional[str] = Field(None, description="Flag image URL")


class CountryCreate(CountryBase):
    """Schema for creating a country"""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name is required and cannot be empty")
        return v.strip()

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None


class CountryUpdate(BaseModel):
    """Schema for updating a country"""

    capital: Optional[str] = None
    region: Optional[str] = None
    population: Optional[int] = Field(None, gt=0)
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = Field(None, ge=0)
    estimated_gdp: Optional[float] = Field(None, ge=0)
    flag_url: Optional[str] = None


class CountryResponse(CountryBase):
    """Schema for country response"""

    id: int
    last_refreshed_at: datetime

    class Config:
        from_attributes = True


class CountryStatusResponse(BaseModel):
    """Schema for status endpoint response"""

    total_countries: int
    last_refreshed_at: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    error: str
    details: Optional[dict | str] = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""

    error: str = "Validation failed"
    details: dict
