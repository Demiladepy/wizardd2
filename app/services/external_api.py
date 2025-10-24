import random
from typing import Dict, List, Optional

import httpx

from app.core.config import settings


class ExternalAPIService:
    """Service for interacting with external APIs"""

    def __init__(self):
        self.timeout = settings.API_TIMEOUT

    async def fetch_countries(self) -> List[Dict]:
        """
        Fetch countries data from restcountries.com

        Returns:
            List of country dictionaries

        Raises:
            httpx.HTTPError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(settings.RESTCOUNTRIES_API_URL)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise Exception(
                "Could not fetch data from restcountries.com - Request timed out"
            )
        except httpx.HTTPError as e:
            raise Exception(f"Could not fetch data from restcountries.com - {str(e)}")
        except Exception as e:
            raise Exception(f"Could not fetch data from restcountries.com - {str(e)}")

    async def fetch_exchange_rates(self) -> Dict[str, float]:
        """
        Fetch exchange rates from open.er-api.com

        Returns:
            Dictionary mapping currency codes to exchange rates

        Raises:
            httpx.HTTPError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(settings.EXCHANGE_RATE_API_URL)
                response.raise_for_status()
                data = response.json()
                return data.get("rates", {})
        except httpx.TimeoutException:
            raise Exception(
                "Could not fetch data from open.er-api.com - Request timed out"
            )
        except httpx.HTTPError as e:
            raise Exception(f"Could not fetch data from open.er-api.com - {str(e)}")
        except Exception as e:
            raise Exception(f"Could not fetch data from open.er-api.com - {str(e)}")

    def calculate_estimated_gdp(
        self, population: int, exchange_rate: Optional[float]
    ) -> Optional[float]:
        """
        Calculate estimated GDP using the formula:
        estimated_gdp = population × random(1000–2000) ÷ exchange_rate

        Args:
            population: Country population
            exchange_rate: Exchange rate to USD

        Returns:
            Estimated GDP or None if exchange_rate is None
        """
        if exchange_rate is None or exchange_rate == 0:
            return None

        random_multiplier = random.uniform(1000, 2000)
        estimated_gdp = (population * random_multiplier) / exchange_rate
        return round(estimated_gdp, 2)

    def extract_currency_code(self, currencies: Optional[List[Dict]]) -> Optional[str]:
        """
        Extract the first currency code from the currencies array

        Args:
            currencies: List of currency dictionaries from the API

        Returns:
            First currency code or None if empty/missing
        """
        if not currencies or not isinstance(currencies, list) or len(currencies) == 0:
            return None

        first_currency = currencies[0]
        if isinstance(first_currency, dict):
            return first_currency.get("code")

        return None

    async def process_country_data(
        self, country_raw: Dict, exchange_rates: Dict[str, float]
    ) -> Dict:
        """
        Process raw country data and combine with exchange rate

        Args:
            country_raw: Raw country data from restcountries.com
            exchange_rates: Dictionary of exchange rates

        Returns:
            Processed country data ready for database storage
        """
        name = country_raw.get("name")
        capital = country_raw.get("capital")
        region = country_raw.get("region")
        population = country_raw.get("population", 0)
        flag_url = country_raw.get("flag")
        currencies = country_raw.get("currencies", [])

        # Extract currency code
        currency_code = self.extract_currency_code(currencies)

        # Get exchange rate
        exchange_rate = None
        if currency_code:
            exchange_rate = exchange_rates.get(currency_code)

        # Calculate estimated GDP
        estimated_gdp = self.calculate_estimated_gdp(population, exchange_rate)

        return {
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url,
        }


# Create a singleton instance
external_api_service = ExternalAPIService()
