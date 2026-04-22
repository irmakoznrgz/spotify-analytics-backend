# Spotify Analytics & Data Engineering API 

An end-to-end data engineering and backend development project. This repository contains an ETL pipeline that transfers 114,000+ Spotify tracks from a Kaggle CSV dataset into a PostgreSQL database, and a fully functional RESTful API built with FastAPI to query and analyze this data.

##  Tech Stack
* **Language:** Python 3.x
* **Database:** PostgreSQL (psycopg2)
* **Data Processing:** Pandas
* **API Framework:** FastAPI & Uvicorn
* **Environment Management:** python-dotenv

##  Key Features
* **ETL Pipeline (`data_importer.py`):** Cleans and migrates raw CSV data (114k rows) into a relational PostgreSQL database automatically.
* **Advanced SQL Queries:** Utilizes complex SQL operations including `GROUP BY`, `ORDER BY`, and **Window Functions** (`ROW_NUMBER()`, `PARTITION BY`).
* **Dynamic Search API:** Allows users to filter tracks dynamically using query parameters (e.g., genre, artist) via FastAPI.

##  Setup and Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/irmakoznrgz/spotify-analytics-backend.git](https://github.com/irmakoznrgz/spotify-analytics-backend.git)
cd spotify-analytics-backend
```

### 3. Database Configuration (.env)
Create a `.env` file in the root directory and add your PostgreSQL credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=your_db_username
DB_PASS=your_db_password
```

### 4. Run the ETL Pipeline (One-Time Setup)
Make sure you have downloaded the dataset from Kaggle and placed it in the `data/` folder. Create your table in PostgreSQL, then run:
```bash
python data_importer.py
```

### 5. Start the FastAPI Server
```bash
uvicorn main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to see the interactive Swagger UI!

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root endpoint, checks API health. |
| `GET` | `/api/stats/artists` | Returns the top 10 most energetic artists. |
| `GET` | `/api/stats/top-songs-by-genre` | Uses Window Functions to return top 3 songs per genre. |
| `GET` | `/api/search` | Dynamic search with 10+ query parameters (genre, energy, danceability, etc.) and pagination support (`limit`, `offset`). |
| `GET` | `/api/search/count` | Returns the total count of tracks matching the active dynamic filters. |
| `GET` | `/api/tracks/{track_id}` | Retrieves all 20 detailed features for a specific single track. |