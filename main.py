from fastapi import FastAPI, Depends, HTTPException
from database import get_db_connection 
import asyncpg

app = FastAPI(title="Spotify Statistics API")

async def get_db():
    conn = await get_db_connection()
    try:
        yield conn 
    finally:
        await conn.close() 

@app.get("/api/stats/artists")
async def get_top_energetic_artists(conn = Depends(get_db)):

    try:
        sql_query = """ 
            SELECT artists, AVG(energy) AS average_energy From spotify_tracks_dataset GROUP BY artists ORDER BY average_energy DESC LIMIT 10;
        """

        coming_data = await conn.fetch(sql_query)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")

    results = []
    for row in coming_data:
        results.append({
            "artist": row[0],
            "average_energy": row[1]
        })
    return results

@app.get("/api/stats/top-songs-by-genre")
async def get_top_songs_by_genre(conn = Depends(get_db)):

    try:
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

        coming_data = await conn.fetch(sql_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")

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
async def search_songs(genre: str = None, 
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
    
    try:
        sql_query = "SELECT track_name, artists, track_genre, popularity, energy, danceability, valence FROM spotify_tracks_dataset WHERE 1=1"
        
        values = []
        
        if genre:
            values.append(genre)
            sql_query += f" AND track_genre = ${len(values)}"
            
            
        if artist:
            search_text = f"%{artist}%"
            values.append(search_text)
            sql_query += f" AND artists ILIKE ${len(values)}"
           

        if track_name:
            search_text = f"%{track_name}%"
            values.append(search_text)
            sql_query += f" AND track_name ILIKE ${len(values)}"
            

        if min_energy is not None:
            values.append(min_energy)
            sql_query += f" AND energy >= ${len(values)}"
            

        if max_energy is not None:
            values.append(max_energy)
            sql_query += f" AND energy <= ${len(values)}"
            

        if min_popularity is not None:
            values.append(min_popularity)
            sql_query += f" AND popularity >= ${len(values)}"
            

        if max_popularity is not None:
            values.append(max_popularity)
            sql_query += f" AND popularity <= ${len(values)}"
            

        if min_danceability is not None:
            values.append(min_danceability)
            sql_query += f" AND danceability >= ${len(values)}"
            
        
        if max_danceability is not None:
            values.append(max_danceability)
            sql_query += f" AND danceability <= ${len(values)}"
           

        if min_valence is not None:
            values.append(min_valence)
            sql_query += f" AND valence >= ${len(values)}"
            

        if max_valence is not None:
            values.append(max_valence)
            sql_query += f" AND valence <= ${len(values)}"
            
        values.append(limit)
        sql_query += f" ORDER BY popularity DESC LIMIT ${len(values)}"
        
        values.append(offset)
        sql_query += f" OFFSET ${len(values)};"

        coming_data = await conn.fetch(sql_query, *values)

    except Exception as e:
        print(f"ERROR FOUND!: {e}") 
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
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
async def filtre_genres(conn = Depends(get_db)):

    try:
        sql_query = """ 
            SELECT DISTINCT track_genre FROM spotify_tracks_dataset;
        """
        coming_data = await conn.fetch(sql_query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")

    results = []
    for row in coming_data:
        results.append(row[0])
    return results


@app.get("/api/search/count")
async def search_songs_count(genre: str = None, 
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
    
    try:
        sql_query = "SELECT COUNT(*) FROM spotify_tracks_dataset WHERE 1=1"
        values = []
        
        if genre:
            values.append(genre)
            sql_query += f" AND track_genre = ${len(values)}"
            
            
        if artist:
            search_text = f"%{artist}%"
            values.append(search_text)
            sql_query += f" AND artists ILIKE ${len(values)}"
            

        if track_name:
            search_text = f"%{track_name}%"
            values.append(search_text)
            sql_query += f" AND track_name ILIKE ${len(values)}"
            

        if min_energy is not None:
            values.append(min_energy)
            sql_query += f" AND energy >= ${len(values)}"
            

        if max_energy is not None:
            values.append(max_energy)
            sql_query += f" AND energy <= ${len(values)}"
           
        if min_popularity is not None:
            values.append(min_popularity)
            sql_query += f" AND popularity >= ${len(values)}"
            

        if max_popularity is not None:
            values.append(max_popularity)
            sql_query += f" AND popularity <= ${len(values)}"
            

        if min_danceability is not None:
            values.append(min_danceability)
            sql_query += f" AND danceability >= ${len(values)}"
            
        
        if max_danceability is not None:
            values.append(max_danceability)
            sql_query += f" AND danceability <= ${len(values)}"
            

        if min_valence is not None:
            values.append(min_valence)
            sql_query += f" AND valence >= ${len(values)}"
            

        if max_valence is not None:
            values.append(max_valence)

            sql_query += f" AND valence <= ${len(values)}"
            
        coming_data = await conn.fetchval(sql_query, *values)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    return {"total_count": coming_data}

@app.get("/api/tracks/{track_id}")
async def get_track_details(track_id: str, conn = Depends(get_db)):
    
    try:
        sql_query = "SELECT * FROM spotify_tracks_dataset WHERE track_id = $1" 

        coming_data = await conn.fetchrow(sql_query, track_id)


    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")

    if not coming_data:
        raise HTTPException(status_code=404, detail="Song Not Found!")
    
    return dict(coming_data)
