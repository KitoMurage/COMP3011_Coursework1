# Pro-Scout API

A RESTful API developed for the COMP3011 Coursework. This system provides a scouting platform for the 2022 World Cup, allowing users to view player data, manage scouting reports, and view performance analytics.

## Project Links
- **Live API Endpoint:** https://kitomurage.pythonanywhere.com/api/scouting-reports/
- **API Documentation (PDF):** ./Pro_Scout_API_Documentation.pdf

## Authentication Credentials
Use the following credentials for HTTP Basic Authentication (required for POST, PUT, DELETE):

- **Username:** `admin`
- **Password:** `Admin123`

## Tech Stack
- **Framework:** Django 5.x
- **Database:** SQLite
- **Data Source:** StatsBomb Open Data (2022 World Cup)
- **Deployment:** PythonAnywhere

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/KitoMurage/COMP3011_Coursework1.git
cd COMP3011_Coursework1
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# On Windows:
# venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Data Ingestion
```bash
python manage.py migrate
python import_statsbomb.py
```

### 5. Run the server locally
```bash
python manage.py runserver
```

The API will be available at: http://127.0.0.1:8000/

## API Features & Endpoints

### HATEOAS Integration
API responses include `_links` to support state transitions and discoverability.

### Security
Sensitive endpoints (POST, PUT, DELETE) are protected via a custom Basic Auth decorator.

### Key Endpoints
- **GET /api/scouting-reports/** – List all scouting reports
- **POST /api/scouting-reports/** – Create a new report (Auth required)
- **GET /api/analytics/leaderboard/** – View top-rated players
- **GET /api/scouting-reports/<id>/** – Retrieve individual report details

## Documentation
The full API specification (including request/response examples and error codes) is available in **Pro_Scout_API_Documentation.pdf**.
