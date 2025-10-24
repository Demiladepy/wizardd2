# Country Currency & Exchange API

A RESTful API built with FastAPI that fetches country data from external sources, combines it with real-time exchange rates, calculates estimated GDP, and provides comprehensive CRUD operations with caching in MySQL.

## 🌟 Features

- **External API Integration**: Fetches country data from [restcountries.com](https://restcountries.com) and exchange rates from [open.er-api.com](https://open.er-api.com)
- **Smart Data Processing**: Automatically matches currencies with exchange rates and calculates estimated GDP
- **MySQL Database**: Persistent storage with efficient caching
- **Advanced Filtering & Sorting**: Filter by region, currency, and sort by multiple criteria
- **Image Generation**: Automatically generates summary images with statistics
- **Comprehensive API**: Full CRUD operations with proper error handling
- **Validation**: Robust input validation with clear error messages
- **Database Migrations**: Alembic-powered schema management

## 📋 Requirements

- Python 3.13 or higher
- MySQL 8.0 or higher
- uv (Fast Python package installer and resolver)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd hng13-stage2-backend
```

### 2. Install uv

If you don't have uv installed:

```bash
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Dependencies

```bash
# uv will automatically create a virtual environment and install dependencies
uv sync
```

Or install specific packages:
```bash
uv pip install fastapi uvicorn sqlalchemy aiomysql pydantic pydantic-settings httpx python-dotenv alembic pillow pymysql
```

### 4. Set Up MySQL Database

```bash
# Create database in MySQL
mysql -u root -p
```

```sql
CREATE DATABASE country_currency_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'country_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON country_currency_db.* TO 'country_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Application Settings
APP_NAME=Country Currency API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# Database Settings (MySQL)
MYSQL_SERVER=localhost
MYSQL_USER=country_user
MYSQL_PASSWORD=secure_password
MYSQL_DB=country_currency_db
MYSQL_PORT=3306
DATABASE_URL=mysql+aiomysql://country_user:secure_password@localhost:3306/country_currency_db

# External API Settings
RESTCOUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_RATE_API_URL=https://open.er-api.com/v6/latest/USD
API_TIMEOUT=30

# Cache Settings
CACHE_DIR=cache
```

### 6. Run Database Migrations

```bash
# Generate initial migration
uv run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
uv run alembic upgrade head
```

### 7. Start the Server

```bash
# Development mode with auto-reload
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
uv run python -m app
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### 1. Refresh Countries Data

**POST** `/countries/refresh`

Fetches all countries from external APIs, processes exchange rates, calculates GDP, and stores in the database. Also generates a summary image.

**Response (200 OK):**
```json
{
    "message": "Countries refreshed successfully",
    "total_countries": 250,
    "created": 200,
    "updated": 50,
    "last_refreshed_at": "2025-10-24T10:30:00Z"
}
```

**Error Response (503):**
```json
{
    "error": "External data source unavailable",
    "details": "Could not fetch data from restcountries.com"
}
```

### 2. Get All Countries

**GET** `/countries`

Retrieve all countries with optional filtering and sorting.

**Query Parameters:**
- `region` (optional): Filter by region (e.g., `Africa`, `Europe`)
- `currency` (optional): Filter by currency code (e.g., `NGN`, `USD`)
- `sort` (optional): Sort order
    - `gdp_desc` - Sort by GDP descending
    - `gdp_asc` - Sort by GDP ascending
    - `name_asc` - Sort by name A-Z
    - `name_desc` - Sort by name Z-A
    - `population_desc` - Sort by population descending
    - `population_asc` - Sort by population ascending

**Example:**
```bash
GET /countries?region=Africa&sort=gdp_desc
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Nigeria",
        "capital": "Abuja",
        "region": "Africa",
        "population": 206139589,
        "currency_code": "NGN",
        "exchange_rate": 1600.23,
        "estimated_gdp": 25767448125.2,
        "flag_url": "https://flagcdn.com/ng.svg",
        "last_refreshed_at": "2025-10-24T10:30:00Z"
    },
    {
        "id": 2,
        "name": "Ghana",
        "capital": "Accra",
        "region": "Africa",
        "population": 31072940,
        "currency_code": "GHS",
        "exchange_rate": 15.34,
        "estimated_gdp": 3029834520.6,
        "flag_url": "https://flagcdn.com/gh.svg",
        "last_refreshed_at": "2025-10-24T10:30:00Z"
    }
]
```

### 3. Get Single Country

**GET** `/countries/{name}`

Get a specific country by name (case-insensitive).

**Example:**
```bash
GET /countries/Nigeria
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-24T10:30:00Z"
}
```

**Error Response (404):**
```json
{
    "error": "Country not found"
}
```

### 4. Delete Country

**DELETE** `/countries/{name}`

Delete a country by name.

**Example:**
```bash
DELETE /countries/Nigeria
```

**Response (200 OK):**
```json
{
    "message": "Country 'Nigeria' deleted successfully"
}
```

### 5. Get API Status

**GET** `/status`

Get total countries count and last refresh timestamp.

**Response (200 OK):**
```json
{
    "total_countries": 250,
    "last_refreshed_at": "2025-10-24T10:30:00Z"
}
```

### 6. Get Summary Image

**GET** `/countries/image`

Serve the generated summary image with statistics.

**Response (200 OK):**
Returns a PNG image with:
- Total number of countries
- Top 5 countries by estimated GDP
- Last refresh timestamp

**Error Response (404):**
```json
{
    "error": "Summary image not found"
}
```

## 🏗️ Project Structure

```
hng13-stage2-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── countries.py        # Country endpoints
│   │   └── status.py           # Status and image endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── database.py         # Database setup and session management
│   ├── crud/
│   │   ├── __init__.py
│   │   └── country.py          # Database operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── country.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── country.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── external_api.py     # External API integration
│   │   └── image_service.py    # Image generation service
│   └── utils/
│       └── __init__.py
├── migrations/
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
├── cache/                      # Generated images directory
├── .env                        # Environment variables (not in repo)
├── .env.example                # Example environment file
├── .gitignore
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Project dependencies
└── README.md
```

## 🔧 Development

### Running Tests

The project includes a **comprehensive test suite** with 80+ tests covering all functionality, edge cases, and requirements.

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test class
pytest tests/test_api_comprehensive.py::TestGetAllCountries -v

# Run tests matching pattern
pytest tests/ -k "currency" -v

# Stop on first failure
pytest tests/ -x

# Using the test runner script
./run_tests.sh all          # Run all tests
./run_tests.sh coverage     # With coverage report
./run_tests.sh fast         # Stop on first failure
./run_tests.sh specific currency  # Run specific tests

# Using Make
make test                   # Run all tests
make test-coverage          # With coverage
make test-fast              # Stop on first failure
```

**Test Coverage:**
- ✅ All 6 endpoints tested
- ✅ All filters and sorting options
- ✅ Currency handling (multiple, missing, unfound)
- ✅ GDP calculation validation
- ✅ Upsert logic (insert vs update)
- ✅ Data validation
- ✅ Error responses (404, 400, 500, 503)
- ✅ Edge cases (special characters, large numbers, etc.)
- ✅ Performance tests
- ✅ Concurrent operations

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

### Code Formatting

```bash
# Format code with black
uv run black app/

# Check code style with ruff
uv run ruff check app/
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current revision
uv run alembic current

# Show migration history
uv run alembic history
```

## 🌐 Deployment

### Deployment Options

This API can be deployed on various platforms:

1. **Railway** (Recommended)
     - Supports MySQL databases
     - Easy deployment from GitHub
     - Automatic HTTPS

2. **Heroku**
     - Use ClearDB MySQL add-on
     - Set environment variables in dashboard

3. **AWS (EC2 + RDS)**
     - EC2 for application
     - RDS for MySQL database
     - Most scalable option

4. **DigitalOcean App Platform**
     - Managed MySQL database
     - Easy setup with Docker

5. **PythonAnywhere**
     - Free tier available
     - MySQL included

### Environment Variables for Production

Ensure these are set in your deployment platform:

```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=mysql+aiomysql://user:password@host:3306/dbname
API_TIMEOUT=30
```

### Railway Deployment Steps

1. **Create a new project on Railway**
2. **Add MySQL database**
     - Railway will provide `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`
3. **Connect GitHub repository**
4. **Set environment variables**
5. **Deploy**

Railway will automatically detect the Python app and install dependencies.

### Docker Deployment (Optional)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
RUN uv sync

COPY . .

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t country-currency-api .
docker run -p 8000:8000 --env-file .env country-currency-api
```

## 📊 Data Processing Logic

### Currency Handling

1. **Multiple Currencies**: If a country has multiple currencies, only the first one is stored
2. **No Currency**: If currencies array is empty:
     - `currency_code` = `null`
     - `exchange_rate` = `null`
     - `estimated_gdp` = `0`
3. **Currency Not Found**: If currency is not in exchange rates API:
     - `exchange_rate` = `null`
     - `estimated_gdp` = `null`

### GDP Calculation

Formula: `estimated_gdp = population × random(1000-2000) ÷ exchange_rate`

- Random multiplier is generated fresh on each refresh
- If `exchange_rate` is `null`, `estimated_gdp` is `null`

### Update Logic

- Countries are matched by name (case-insensitive)
- Existing countries are updated with new data
- New countries are inserted
- All fields are recalculated including GDP with new random multiplier

## ❗ Error Handling

All errors return consistent JSON responses:

```json
{
    "error": "Error type",
    "details": "Detailed error message"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (external API failure)

## 🔍 Validation Rules

- `name`: Required, non-empty string
- `population`: Required, must be positive integer
- `currency_code`: Optional, but required for GDP calculation
- `exchange_rate`: Must be non-negative if provided
- `estimated_gdp`: Must be non-negative if provided

## 📝 License

MIT License - feel free to use this project for learning and development.

## 👨‍💻 Author

Built with ❤️ for HNG13 Stage 2 Backend Task

## 🙏 Acknowledgments

- [restcountries.com](https://restcountries.com) - Country data API
- [open.er-api.com](https://open.er-api.com) - Exchange rates API
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

## 📞 Support

If you encounter any issues:
1. Check the logs for detailed error messages
2. Verify environment variables are set correctly
3. Ensure MySQL database is running and accessible
4. Check external APIs are accessible from your server

---

**Happy Coding! 🚀**
