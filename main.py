from fastapi import FastAPI, Depends
from database import get_db_connection 

app = FastAPI(title="Spotify Statistics API")

def get_db():
    conn = get_db_connection()
    try:
        yield conn 
    finally:
        conn.close() 

@app.get("/api/stats/artists")
def get_top_energetic_artists(conn = Depends(get_db)):
    cursor = conn.cursor()

    sql_query = """ 
        SELECT artists, AVG(energy) AS average_energy From spotify_tracks_dataset GROUP BY artists ORDER BY average_energy DESC LIMIT 10;
    """

    cursor.execute(sql_query)

    comeing_data = cursor.fetchall()
    cursor.close()

    results = []
    for row in comeing_data:
        results.append({
            "artist": row[0],
            "average_energy": row[1]
        })
    return results

@app.get("/api/stats/top-songs-by-genre")
def get_top_songs_by_genre(conn = Depends(get_db)):
    cursor = conn.cursor()

    sql_query = """ 
        WITH RankedData AS (
            SELECT 
                track_name, 
                artists, 
                track_genre, 
                popularity,
                ROW_NUMBER() OVER (PARTITION BY track_genre ORDER BY popularity DESC) AS most_popular 
            FROM spotify_tracks_dataset
        )
        SELECT 
            track_name, 
            artists, 
            track_genre, 
            popularity
        FROM RankedData
        WHERE most_popular IN (1,2,3);
    """

    cursor.execute(sql_query)
    coming_data = cursor.fetchall()
    cursor.close()

    results = []
    for row in coming_data:
        results.append({
            "track_name": row[0],
            "artist": row[1],
            "genre": row[2],
            "popularity": row[3]
        })
    return results


@app.get("/api/search")
def search_songs(genre: str = None, artist: str = None, conn = Depends(get_db)):
    
    cursor = conn.cursor()

    sql_query = "SELECT track_name, artists, track_genre, popularity FROM spotify_tracks_dataset WHERE 1=1"
    
    values = []
    
    if genre:
        sql_query += " AND track_genre = %s"
        values.append(genre)
        
    if artist:
        sql_query += " AND artists ILIKE %s"
        search_text = f"%{artist}%"
        values.append(search_text)

    sql_query += " ORDER BY popularity DESC LIMIT 50;"

    cursor.execute(sql_query, values)
    coming_data = cursor.fetchall()
    cursor.close()
    
    results = []
    for row in coming_data:
        results.append({
            "track_name": row[0],
            "artist": row[1],
            "genre": row[2],
            "popularity": row[3]
        })
    return results