from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.country import Country


class CountryCRUD:
    """CRUD operations for Country model"""

    async def create(self, db: AsyncSession, country_data: Dict) -> Country:
        """
        Create a new country record

        Args:
            db: Database session
            country_data: Dictionary with country data

        Returns:
            Created Country instance
        """
        country = Country(**country_data)
        db.add(country)
        await db.flush()
        await db.refresh(country)
        return country

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Country]:
        """
        Get a country by name (case-insensitive)

        Args:
            db: Database session
            name: Country name

        Returns:
            Country instance or None
        """
        result = await db.execute(
            select(Country).where(func.lower(Country.name) == name.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, country_id: int) -> Optional[Country]:
        """
        Get a country by ID

        Args:
            db: Database session
            country_id: Country ID

        Returns:
            Country instance or None
        """
        result = await db.execute(select(Country).where(Country.id == country_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Country]:
        """
        Get all countries with optional filters and sorting

        Args:
            db: Database session
            region: Filter by region
            currency: Filter by currency code
            sort: Sort order (gdp_desc, gdp_asc, name_asc, name_desc, population_desc, population_asc)

        Returns:
            List of Country instances
        """
        query = select(Country)

        # Apply filters
        if region:
            query = query.where(func.lower(Country.region) == region.lower())

        if currency:
            query = query.where(func.lower(Country.currency_code) == currency.lower())

        # Apply sorting
        if sort:
            sort_lower = sort.lower()
            if sort_lower == "gdp_desc":
                query = query.order_by(desc(Country.estimated_gdp))
            elif sort_lower == "gdp_asc":
                query = query.order_by(Country.estimated_gdp)
            elif sort_lower == "name_asc":
                query = query.order_by(Country.name)
            elif sort_lower == "name_desc":
                query = query.order_by(desc(Country.name))
            elif sort_lower == "population_desc":
                query = query.order_by(desc(Country.population))
            elif sort_lower == "population_asc":
                query = query.order_by(Country.population)
            else:
                # Default sort by name
                query = query.order_by(Country.name)
        else:
            # Default sort by name
            query = query.order_by(Country.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, country: Country, update_data: Dict
    ) -> Country:
        """
        Update a country record

        Args:
            db: Database session
            country: Country instance to update
            update_data: Dictionary with updated data

        Returns:
            Updated Country instance
        """
        for key, value in update_data.items():
            if hasattr(country, key):
                setattr(country, key, value)

        country.last_refreshed_at = datetime.utcnow()
        await db.flush()
        await db.refresh(country)
        return country

    async def delete(self, db: AsyncSession, country: Country) -> None:
        """
        Delete a country record

        Args:
            db: Database session
            country: Country instance to delete
        """
        await db.delete(country)
        await db.flush()

    async def get_count(self, db: AsyncSession) -> int:
        """
        Get total count of countries

        Args:
            db: Database session

        Returns:
            Total number of countries
        """
        result = await db.execute(select(func.count(Country.id)))
        return result.scalar_one()

    async def get_last_refreshed(self, db: AsyncSession) -> Optional[datetime]:
        """
        Get the most recent last_refreshed_at timestamp

        Args:
            db: Database session

        Returns:
            Most recent timestamp or None
        """
        result = await db.execute(select(func.max(Country.last_refreshed_at)))
        return result.scalar_one_or_none()

    async def get_top_by_gdp(self, db: AsyncSession, limit: int = 5) -> List[Country]:
        """
        Get top countries by estimated GDP

        Args:
            db: Database session
            limit: Number of countries to return

        Returns:
            List of top Country instances
        """
        result = await db.execute(
            select(Country)
            .where(Country.estimated_gdp.isnot(None))
            .order_by(desc(Country.estimated_gdp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert(
        self, db: AsyncSession, country_data: Dict
    ) -> tuple[Country, bool]:
        """
        Update existing country or create new one

        Args:
            db: Database session
            country_data: Dictionary with country data

        Returns:
            Tuple of (Country instance, is_new)
        """
        existing = await self.get_by_name(db, country_data["name"])

        if existing:
            # Update existing
            updated = await self.update(db, existing, country_data)
            return updated, False
        else:
            # Create new
            created = await self.create(db, country_data)
            return created, True


# Create a singleton instance
country_crud = CountryCRUD()
