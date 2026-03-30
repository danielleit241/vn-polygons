# VN Polygons API

## 📖 Project Introduction

**VN Polygons API** is a backend service providing administrative data for Vietnam and geographical polygons for provinces and cities. The project adopts an API-first approach, focusing on CRUD operations for administrative entities and importing GeoJSON data into a PostgreSQL database.

### Project Scope

The current system provides the following capabilities:

- Manage Administrative Regions, Administrative Units, Provinces, and Wards.
- Store province polygons within the boundary_geojson field.
- Import polygons from existing GeoJSON file sets.
- Provide REST APIs with Swagger/OpenAPI documentation.

---

## ✨ Core Features

### 1) Administrative Data APIs

- CRUD operations for administrative regions, administrative units, provinces, and wards.
- Support for pagination and filtering wards by province_code.

### 2) Province Polygon Import

- Import from the directory specified by PROVINCE_POLYGONS_DIR.
- Mechanism to map files by code_name with a fallback to slug.
- Optional overwrite feature to overwrite existing polygons.

### 3) Data Validation and Consistency

- Request/response validation using Pydantic schemas.
- Validate foreign keys to administrative_units and provinces before writing data.
- Return explicit HTTP error messages for 400/404 scenarios.

### 4) Testing and Quality Gate

- Unit tests for the service layer.
- Enforced minimum of 80% test coverage for app/services.

---

## 🛠️ Technology Stack

**Backend:**

- FastAPI
- Uvicorn
- Python 3.12+

**Data Layer:**

- PostgreSQL 16
- SQLAlchemy 2.x
- psycopg 3

**Validation and Configuration:**

- Pydantic / pydantic-settings
- python-dotenv

**Testing:**

- pytest
- pytest-cov

---

## 📁 Source Code Overview

`	ext
vn-polygons/
|-- app/
|   |-- main.py                         # FastAPI app entrypoint
|   |-- api/v1/
|   |   |-- router.py                   # Main API router
|   |   -- endpoints/                  # Resource endpoints
|   |-- core/config.py                  # Environment settings (.env)
|   |-- db/session.py                   # Engine & SessionLocal setup
|   |-- models/                         # SQLAlchemy models
|   |-- schemas/                        # Pydantic validation schemas
|   -- services/                       # Business logic layer
|-- sql/
|   |-- schema.sql                      # Create tables/indexes/constraints
|   |-- seed-data.sql                   # Initial seed data
|   -- provinces/*.json                # GeoJSON polygon sets
|-- tests/
|   |-- conftest.py
|   -- test_services.py
|-- docker-compose.yml
|-- Dockerfile
|-- requirements.txt
|-- pytest.ini
-- .env.example
`

---

## 🏗️ Architecture and Request Flow

**Request Flow**  
Client -> FastAPI Router -> Service/ORM -> PostgreSQL -> Response

**Layer Responsibilities**

- **Router Layer (app/api/v1/endpoints)**: Receives requests, validates query/path/body, and formats HTTP status codes and responses.
- **Service Layer (app/services)**: Encapsulates business logic (especially polygon imports) and handles candidate mapping and import results.
- **Data Layer (app/models, app/db)**: ORM model mapping, session management, and transaction commits/rollbacks.

---

## 📊 Data Model Summary

- **administrative_regions**: id (PK), name, name_en, code_name, code_name_en
- **administrative_units**: id (PK), full_name, full_name_en, short_name, short_name_en, code_name, code_name_en
- **provinces**: code (PK), name, name_en, full_name, full_name_en, code_name, boundary_geojson (JSON/JSONB), administrative_unit_id (FK)
- **wards**: code (PK), name, name_en, full_name, full_name_en, code_name, province_code (FK), administrative_unit_id (FK)

---

## ⚙️ Environment Configuration

Create a .env file from the template:
`powershell
copy .env.example .env
`

**Default Content:**
`env
APP_NAME=VN Polygons API
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/vn_polygons
PROVINCE_POLYGONS_DIR=sql/provinces
`

---

## 🚀 Run Options

### Option 1: Run with Docker Compose

**Start services:**
`powershell
copy .env.example .env
docker compose up --build -d
`
_Defaults:_ API: http://localhost:8000 | PostgreSQL: localhost:5432  
_(Database init scripts schema.sql & seed-data.sql are mounted and run on the first volume creation)._

**Useful commands:**
`powershell
docker compose ps
docker compose logs -f api
docker compose logs -f db
docker compose down
docker compose down -v   # Stops containers and removes volumes
`

### Option 2: Run locally

**Setup virtual environment and dependencies:**
`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
`

**Start the application:**
`powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
`

---

## 📚 API Documentation

Once the server is running, access the documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔌 Endpoint Matrix

### System

| Method | Endpoint       | Description  |
| ------ | -------------- | ------------ |
| GET    | /              | Root message |
| GET    | /api/v1/health | Health check |

### Administrative Units & Regions

| Group       | Base Endpoint                  | Features                                |
| ----------- | ------------------------------ | --------------------------------------- |
| **Regions** | /api/v1/administrative-regions | List, Get By ID, Create, Update, Delete |
| **Units**   | /api/v1/administrative-units   | List, Get By ID, Create, Update, Delete |

### Provinces & Wards

| Group         | Base Endpoint     | Features                                                                 |
| ------------- | ----------------- | ------------------------------------------------------------------------ |
| **Provinces** | /api/v1/provinces | List, Get By Code, Create, Update, Delete <br> **POST** /polygons/import |
| **Wards**     | /api/v1/wards     | List, Get By Code, Create, Update, Delete                                |

---

## 📝 Request Examples

### Create a Province

`ash
curl -X POST "http://localhost:8000/api/v1/provinces" \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"01\",
    \"name\": \"Ha Noi\",
    \"name_en\": \"Hanoi\",
    \"full_name\": \"Thanh pho Ha Noi\",
    \"full_name_en\": \"Hanoi City\",
    \"code_name\": \"ha_noi\",
    \"administrative_unit_id\": 1
  }"
`

### Import Polygons

`ash
curl -X POST "http://localhost:8000/api/v1/provinces/polygons/import?overwrite=false"
`
**Example Response:**
`json
{
  "updated": 34,
  "missing_files": [],
  "failed_files": []
}
`

**Polygon Import Rules**  
The system looks for polygon files in the following order:

1. province.code_name
2. Slug format of province.name
3. Slug format of province.name_en
4. _Special case:_ ho_chi_minh -> tp_ho_chi_minh.json

_Note: Only the geometry from the first feature in the GeoJSON file is extracted. If overwrite=false, existing records will be skipped._

---

## 🧪 Testing

**Run all tests:**
`powershell
pytest
`

**Run service tests only:**
`powershell
pytest -q tests/test_services.py
`

_Test Coverage Policy (configured in pytest.ini)_: targets app/services with a minimum threshold of **80%**.

---

## 🔧 Troubleshooting

- **DB connection failed**: Check DATABASE_URL in .env. If using Docker, ensure the db container is healthy and port 5432 is not conflicting.
- **API cannot start**: Ensure the virtual environment is activated, dependencies are fully installed, or check logs using docker compose logs -f api.
- **Init SQL did not apply**: Init scripts only run upon fresh volume creation. Run docker compose down -v and then bring it back up.
- **Polygon import returns missing_files**: Check PROVINCE_POLYGONS_DIR. Verify the naming conventions in sql/provinces match code_name or slugs.

---

## 🛡️ Security and Operations Notes

- Do **not** commit the .env file to version control.
- Avoid exposing the database directly outside the production network.
- Deploy behind a reverse proxy map with TLS for production domains.
- Configure solid monitoring and backup strategies for PostgreSQL.

---

## 📄 License

Currently, no LICENSE is declared. If this project is made public or distributed, an appropriate LICENSE file should be added.
