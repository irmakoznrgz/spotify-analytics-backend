from database import get_db_connection
import pandas as pd
import asyncpg
import asyncio

# Pandas reads CSV files
df = pd.read_csv('data/spotify-tracks-dataset.csv')

#Delete empty data with pandas
df_cleaned = df.dropna()
df_cleaned = df_cleaned.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], errors='ignore')

async def run_importer():
    conn = None
    try:
        conn = await get_db_connection()

        async with conn.transaction():

            # "$1, $2" = Native Placeholder
            for index, row in df_cleaned.iterrows():
                sql = """
                    INSERT INTO spotify_tracks_dataset (track_id, artists, album_name, track_name, popularity, duration_ms, explicit, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature, track_genre) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20) 
                """

                values = (row['track_id'], row['artists'], row['album_name'], row['track_name'], row['popularity'], row['duration_ms'], row['explicit'], row['danceability'], row['energy'], row['key'], row['loudness'], row['mode'], row['speechiness'], row['acousticness'], row['instrumentalness'], row['liveness'], row['valence'], row['tempo'], row['time_signature'], row['track_genre'])

                await conn.execute(sql, *values)

            print("Data has been successfully entered into the database.")

    except Exception as e: 
        print(f"ERROR: {e}")

    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(run_importer())