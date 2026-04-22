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

    coming_data = cursor.fetchall()
    cursor.close()

    results = []
    for row in coming_data:
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
def search_songs(genre: str = None, 
                artist: str = None, 
                track_name: str = None,
                min_energy: float = None, 
                max_energy: float = None, 
                min_danceability: float = None,
                max_danceability: float = None,
                min_popularity: float = None,
                max_popularity: float = None,
                min_valence: float = None,
                max_valence: float = None,
                limit: int = 50,
                offset: int = 0,
                conn = Depends(get_db)):
    
    cursor = conn.cursor()

    sql_query = "SELECT track_name, artists, track_genre, popularity, energy, danceability, valence FROM spotify_tracks_dataset WHERE 1=1"
    
    values = []
    
    if genre:
        sql_query += " AND track_genre = %s"
        values.append(genre)
        
    if artist:
        sql_query += " AND artists ILIKE %s"
        search_text = f"%{artist}%"
        values.append(search_text)

    if track_name:
        sql_query += " AND track_name ILIKE %s"
        search_text = f"%{track_name}%"
        values.append(search_text)

    if min_energy is not None:
        sql_query += " AND energy >= %s"
        values.append(min_energy)

    if max_energy is not None:
        sql_query += " AND energy <= %s"
        values.append(max_energy)

    if min_popularity is not None:
        sql_query += " AND popularity >= %s"
        values.append(min_popularity)

    if max_popularity is not None:
        sql_query += " AND popularity <= %s"
        values.append(max_popularity)

    if min_danceability is not None:
        sql_query += " AND danceability >= %s"
        values.append(min_danceability)
    
    if max_danceability is not None:
        sql_query += " AND danceability <= %s"
        values.append(max_danceability)

    if min_valence is not None:
        sql_query += " AND valence >= %s"
        values.append(min_valence)

    if max_valence is not None:
        sql_query += " AND valence <= %s"
        values.append(max_valence)

    sql_query += " ORDER BY popularity DESC LIMIT %s OFFSET %s;"
    values.append(limit)
    values.append(offset)

    cursor.execute(sql_query, values)
    coming_data = cursor.fetchall()
    cursor.close()
    
    results = []
    for row in coming_data:
        results.append({
            "track_name": row[0],
            "artist": row[1],
            "genre": row[2],
            "popularity": row[3],
            "energy": row[4],
            "danceability": row[5],
            "valence": row[6]
        })
    return results

@app.get("/api/genres")
def filtre_genres(conn = Depends(get_db)):

    cursor = conn.cursor()

    sql_query = """ 
        SELECT DISTINCT track_genre FROM spotify_tracks_dataset;
    """
    cursor.execute(sql_query)
    coming_data = cursor.fetchall()
    cursor.close()

    results = []
    for row in coming_data:
        results.append(row[0])
    return results


@app.get("/api/search/count")
def search_songs_count(genre: str = None, 
                artist: str = None, 
                track_name: str = None,
                min_energy: float = None, 
                max_energy: float = None, 
                min_danceability: float = None,
                max_danceability: float = None,
                min_popularity: float = None,
                max_popularity: float = None,
                min_valence: float = None,
                max_valence: float = None,
                conn = Depends(get_db)):
    
    cursor = conn.cursor()

    sql_query = "SELECT COUNT(*) FROM spotify_tracks_dataset WHERE 1=1"
    values = []
    
    if genre:
        sql_query += " AND track_genre = %s"
        values.append(genre)
        
    if artist:
        sql_query += " AND artists ILIKE %s"
        search_text = f"%{artist}%"
        values.append(search_text)

    if track_name:
        sql_query += " AND track_name ILIKE %s"
        search_text = f"%{track_name}%"
        values.append(search_text)

    if min_energy is not None:
        sql_query += " AND energy >= %s"
        values.append(min_energy)

    if max_energy is not None:
        sql_query += " AND energy <= %s"
        values.append(max_energy)

    if min_popularity is not None:
        sql_query += " AND popularity >= %s"
        values.append(min_popularity)

    if max_popularity is not None:
        sql_query += " AND popularity <= %s"
        values.append(max_popularity)

    if min_danceability is not None:
        sql_query += " AND danceability >= %s"
        values.append(min_danceability)
    
    if max_danceability is not None:
        sql_query += " AND danceability <= %s"
        values.append(max_danceability)

    if min_valence is not None:
        sql_query += " AND valence >= %s"
        values.append(min_valence)

    if max_valence is not None:
        sql_query += " AND valence <= %s"
        values.append(max_valence)

    cursor.execute(sql_query, values)
    coming_data = cursor.fetchone()
    cursor.close()
    
    return {"total_count": coming_data[0]}

@app.get("/api/tracks/{track_id}")
def get_track_details(track_id: str, conn = Depends(get_db)):
    
    cursor = conn.cursor()

    sql_query = "SELECT * FROM spotify_tracks_dataset WHERE track_id = %s" 

    cursor.execute(sql_query, (track_id,))
    coming_data = cursor.fetchone()
    cursor.close()

    if not coming_data:
        return {"ERROR": "Song Not Found!"}

    col_name = [desc[0] for desc in cursor.description]
    song_detail = dict(zip(col_name, coming_data))
    
    return song_detail