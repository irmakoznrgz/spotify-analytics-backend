import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Spotify Analytics Explorer", page_icon="🎧", layout="wide")

# --- API BASE URL ---
API_BASE_URL = "http://127.0.0.1:8000/api"

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600) # Caches the genres so we don't hit the DB every second
def get_genres():
    try:
        response = requests.get(f"{API_BASE_URL}/genres")
        if response.status_code == 200:
            return ["All"] + response.json()
    except:
        pass
    return ["All", "pop", "rock", "hip-hop", "classical"] # Fallback

# --- UI: SIDEBAR FILTERS ---
st.sidebar.header("🎛️ Audio Features Filters")

# Genre Dropdown
genres_list = get_genres()
selected_genre = st.sidebar.selectbox("Select Genre", genres_list)

# Range Sliders with Default Values
energy_range = st.sidebar.slider("Energy", min_value=0.0, max_value=1.0, value=(0.0, 1.0), step=0.01)
danceability_range = st.sidebar.slider("Danceability", min_value=0.0, max_value=1.0, value=(0.0, 1.0), step=0.01)
valence_range = st.sidebar.slider("Valence (Happiness)", min_value=0.0, max_value=1.0, value=(0.0, 1.0), step=0.01)
popularity_range = st.sidebar.slider("Popularity", min_value=0, max_value=100, value=(0, 100), step=1)

# --- UI: TOP SEARCH BAR ---
st.title("🎧 Spotify Analytics Explorer")
st.markdown("Search tracks, filter by audio features, and visualize data.")

col1, col2 = st.columns(2)
artist_search = col1.text_input("🔍 Search Artist", placeholder="e.g., Eminem")
track_search = col2.text_input("🎵 Search Track Name", placeholder="e.g., Lose Yourself")

# We use a form so the page doesn't refresh on every slider move, only when "Find Tracks" is clicked.
with st.sidebar.form("search_form"):
    search_button = st.form_submit_button("🔍 Find Tracks")

# --- MAIN LOGIC ---
if search_button:
    # 1. Build Query Parameters
    params = {
        "min_energy": energy_range[0],
        "max_energy": energy_range[1],
        "min_danceability": danceability_range[0],
        "max_danceability": danceability_range[1],
        "min_valence": valence_range[0],
        "max_valence": valence_range[1],
        "min_popularity": popularity_range[0],
        "max_popularity": popularity_range[1],
        "limit": 50,
        "offset": 0
    }
    
    if selected_genre != "All":
        params["genre"] = selected_genre
    if artist_search:
        params["artist"] = artist_search
    if track_search:
        params["track_name"] = track_search

    # 2. Fetch Total Count
    count_res = requests.get(f"{API_BASE_URL}/search/count", params=params)
    total_tracks = count_res.json().get("total_count", 0) if count_res.status_code == 200 else 0

    st.success(f"**{total_tracks}** tracks found matching your criteria!")

    # 3. Fetch Data
    with st.spinner("Fetching tracks from database..."):
        tracks_res = requests.get(f"{API_BASE_URL}/search", params=params)
        
        if tracks_res.status_code == 200 and tracks_res.json():
            df = pd.DataFrame(tracks_res.json())
            
            # Save to session state so it doesn't disappear when interacting with the chart
            st.session_state['search_results'] = df
        else:
            st.warning("No tracks found or backend is unreachable.")
            st.session_state['search_results'] = pd.DataFrame()

# --- DISPLAY RESULTS & CHARTS ---
if 'search_results' in st.session_state and not st.session_state['search_results'].empty:
    df = st.session_state['search_results']
    
    st.subheader("📋 Track Results")
    st.dataframe(df, use_container_width=True)

    # --- TRACK DETAILS SECTION (GOOGLE SEARCH) ---
    st.subheader("🔍 Explore Track")
    st.markdown("Select a track from the results to search for it on Google.")
    
    if "track_id" in df.columns:
        track_options = df['track_id'].tolist()
        format_func = lambda x: df.loc[df['track_id'] == x, 'track_name'].values[0] + " - " + df.loc[df['track_id'] == x, 'artist'].values[0]
        
        selected_track_id = st.selectbox("Choose a track", track_options, format_func=format_func)
        
        if selected_track_id:
            # Seçilen şarkının adını ve sanatçısını bulalım
            track_name = df.loc[df['track_id'] == selected_track_id, 'track_name'].values[0]
            artist_name = df.loc[df['track_id'] == selected_track_id, 'artist'].values[0]
            
            # Google arama URL'sini oluşturalım (Boşlukları + işaretine çeviriyoruz)
            search_query = f"{track_name} {artist_name}".replace(" ", "+")
            google_url = f"https://www.google.com/search?q={search_query}"
            
            # Markdown ile şık bir tıklanabilir buton (link) oluşturuyoruz
            st.markdown(
                f'<a href="{google_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #1DB954; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">🌍 Search "{track_name}" on Google</a>',
                unsafe_allow_html=True
            )
    else:
        st.info("⚠️ Note: Still waiting for 'track_id' to arrive from the backend.")
    
    # Check if 'track_id' is in the dataframe. If your backend doesn't return it yet, fallback to track_name.
    if "track_id" in df.columns:
        track_options = df['track_id'].tolist()
        format_func = lambda x: df.loc[df['track_id'] == x, 'track_name'].values[0] + " - " + df.loc[df['track_id'] == x, 'artist'].values[0]
        
        selected_track_id = st.selectbox("Choose a track", track_options, format_func=format_func)
        
        if selected_track_id:
            detail_res = requests.get(f"{API_BASE_URL}/tracks/{selected_track_id}")
            if detail_res.status_code == 200:
                details = detail_res.json()
                
                # Display details in a nice card format
                col_d1, col_d2, col_d3 = st.columns(3)
                col_d1.metric("Tempo", f"{details.get('tempo', 0):.1f} BPM")
                col_d2.metric("Liveness", details.get('liveness', 0))
                col_d3.metric("Acousticness", details.get('acousticness', 0))
                
                with st.expander("Show Full Raw Data"):
                    st.json(details)
    else:
        st.info("⚠️ Note: To see track details, add 'track_id' to your backend /api/search endpoint SELECT statement.")

    # --- CHARTS SECTION ---
    st.markdown("---")
    st.subheader("📈 Audio Features Analysis")
    
    # Line Chart for Audio Features
    st.markdown("Comparison of Energy, Danceability, and Valence across the retrieved tracks.")
    # We melt the dataframe to make it suitable for Plotly Line Charts
    df_features = df[['track_name', 'energy', 'danceability', 'valence']]
    df_melted = df_features.melt(id_vars='track_name', var_name='Feature', value_name='Value')
    
    fig = px.line(df_melted, x='track_name', y='Value', color='Feature', markers=True, title="Audio Features Line Chart")
    fig.update_xaxes(showticklabels=False) # Hide x-axis labels if there are too many tracks
    st.plotly_chart(fig, use_container_width=True)