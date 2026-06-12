# ETL Lab - Rick & Morty API

## Description

Complete ETL pipeline that extracts data from the Rick & Morty public API, stores it in MongoDB, transforms it using Pandas, and loads it into MySQL. It includes RESTful endpoints with FastAPI to execute the pipeline and query statistical analysis.

## Features

- Idempotent extraction from external API
- Storage in MongoDB (staging layer)
- Transformation with Pandas (flattening of nested JSONs)
- Idempotent load to MySQL with ON DUPLICATE KEY UPDATE
- Dynamic type detection for column analysis
- Dual Profile to compare records between MongoDB and MySQL
- Reset with TRUNCATE (not DROP)
- 11 columns in MySQL (exceeds the minimum of 8)

## Technologies

| Technology | Version | Purpose |
|------------|---------|-----------|
| Python | 3.9+ | Main language |
| FastAPI | 0.104.1 | Web framework |
| MongoDB | 5.0+ | NoSQL database (staging) |
| MySQL | 8.0+ | SQL database (data warehouse) |
| Pandas | 2.1.3 | Data transformation |
| SQLAlchemy | 2.0.23 | ORM for MySQL |
| Uvicorn | 0.24.0 | ASGI server |

## Project Structure

```text
laboratorio_etl/
├── .env                        # Environment variables
├── .gitignore                  # Ignored files and folders
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── app/
    ├── main.py                 # FastAPI application entry point
    ├── config.py               # Database and environment configuration
    ├── database.py             # MongoDB and MySQL connection setups
    ├── controllers/            # ETL and analytics endpoints
    ├── etl_controller.py       # ETL endpoints and routing
    ├── analitica_controller.py # Analytics endpoints and routing
    ├── services/               # Business logic
    │   ├── etl_service.py      # Core ETL business logic
    │   └── analitica_service.py # Analytics business logic
    ├── models/
    │   └── personajes_sql.py   # SQLAlchemy model definition
    └── views/
        └── schemas.py          # Pydantic schemas for data validation
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lauratoro1/laboratorio_elt.git
cd laboratorio_elt
```

### 2. Create and activate a virtual environment

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Copy the example environment file

```bash
# Linux/Mac
cp example.env .env

# Windows (Command Prompt)
copy example.env .env

# Windows (PowerShell)
cp example.env .env
```

### 5. Create the MySQL database

Log into your MySQL server and run the following command to create the database:

```sql
-- Database creation
CREATE DATABASE rickmorty_dw;
```

#### Alternative via terminal:

```bash
# Linux / Mac / Windows (Git Bash or PowerShell)
mysql -u root -p -e "CREATE DATABASE rickmorty_dw;"

# Windows (Command Prompt)
mysql -u root -p -e "CREATE DATABASE rickmorty_dw;"
```

### 6. Run the application

Start the FastAPI development server using Uvicorn:

```bash
uvicorn app.main:app --reload 
```

Once the server is running, you can access:
- The API interactive documentation (Swagger UI): `http://localhost:8000/docs`
- The alternative documentation (ReDoc): `http://localhost:8000/redoc`

## Usage Examples

### ETL Operations

#### Extract 50 characters

```bash
curl -X POST http://localhost:8000/api/v1/etl/extract \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 50}'
```

#### Transform and load

```bash
curl -X POST http://localhost:8000/api/v1/etl/transform
```

#### System reset (clean all data)

```bash
curl -X DELETE http://localhost:8000/api/v1/etl/reset
```

#### Debug reset (clean and view function output)

```bash
curl http://localhost:8000/api/v1/etl/debug-reset
```

### Analytics Services

#### Column analysis

```bash
# Species analysis
curl "http://localhost:8000/api/v1/analytics/column/species"

# Status analysis
curl "http://localhost:8000/api/v1/analytics/column/status"

# Total episodes analysis
curl "http://localhost:8000/api/v1/analytics/column/total_episodes"

# Gender analysis
curl "http://localhost:8000/api/v1/analytics/column/gender"

# Boolean flag analysis
curl "http://localhost:8000/api/v1/analytics/column/has_special_type"
```

#### Dual Profile comparison

```bash
# Compare character 1 across MongoDB and MySQL
curl "http://localhost:8000/api/v1/profile/1"

# Compare character 2 across MongoDB and MySQL
curl "http://localhost:8000/api/v1/profile/2"
```

#### Advanced statistics

```bash
# General summary metrics
curl "http://localhost:8000/api/v1/analytics/summary"

# Status breakdown metrics
curl "http://localhost:8000/api/v1/analytics/status"

# Top 5 species metrics
curl "http://localhost:8000/api/v1/analytics/species?limit=5"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

