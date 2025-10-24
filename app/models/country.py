from datetime import datetime
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Country(Base):
    """Country model for storing country data with exchange rates"""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    capital: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, index=True
    )
    exchange_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(20, 6), nullable=True
    )
    estimated_gdp: Mapped[Optional[float]] = mapped_column(
        DECIMAL(30, 2), nullable=True, index=True
    )
    flag_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_refreshed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Country(name={self.name}, region={self.region}, currency={self.currency_code})>"
