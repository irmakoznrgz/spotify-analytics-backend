from database import get_db_connection
import pandas as pd

# Pandas reads CSV files
df = pd.read_csv('data/spotify-tracks-dataset.csv')

#Delete empty data with pandas
df_cleaned = df.dropna()
df_cleaned = df_cleaned.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], errors='ignore')

conn = get_db_connection()
cursor = conn.cursor()

# "s%" = placeholder
for index, row in df_cleaned.iterrows():
    sql = """
        INSERT INTO spotify_tracks_dataset (track_id, artists, album_name, track_name, popularity, duration_ms, explicit, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature, track_genre) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """

    values = (row['track_id'], row['artists'], row['album_name'], row['track_name'], row['popularity'], row['duration_ms'], row['explicit'], row['danceability'], row['energy'], row['key'], row['loudness'], row['mode'], row['speechiness'], row['acousticness'], row['instrumentalness'], row['liveness'], row['valence'], row['tempo'], row['time_signature'], row['track_genre'])

    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()
