import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Spotify Analyzer Statistics", page_icon="🎧", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000/api"

# SESSION STATE INITIALIZATION 
if 'offset' not in st.session_state:
    st.session_state['offset'] = 0
if 'search_params' not in st.session_state:
    st.session_state['search_params'] = {}
if 'total_tracks' not in st.session_state:
    st.session_state['total_tracks'] = 0

@st.cache_data(ttl=3600)
def get_genres():
    try:
        response = requests.get(f"{API_BASE_URL}/genres")
        if response.status_code == 200:
            return ["All"] + response.json()
    except:
        pass
    return ["All", "pop", "rock", "hip-hop", "classical"]

def fetch_and_update_data(params, new_offset):
    params['offset'] = new_offset
    params['limit'] = 10 
    
    count_res = requests.get(f"{API_BASE_URL}/search/count", params=params)
    total = count_res.json().get("total_count", 0) if count_res.status_code == 200 else 0
    st.session_state['total_tracks'] = total

    tracks_res = requests.get(f"{API_BASE_URL}/search", params=params)
    if tracks_res.status_code == 200 and tracks_res.json():
        st.session_state['search_results'] = pd.DataFrame(tracks_res.json())
    else:
        st.session_state['search_results'] = pd.DataFrame()
        
    st.session_state['search_params'] = params
    st.session_state['offset'] = new_offset

st.sidebar.header("Filters")

genres_list = get_genres()
selected_genre = st.sidebar.selectbox("Select Genre", genres_list)

# Tooltips
energy_range = st.sidebar.slider("Energy", 0.0, 1.0, (0.0, 1.0), 0.01, help="0.0 represents calm/acoustic tracks, 1.0 represents fast/loud energetic tracks.")
danceability_range = st.sidebar.slider("Danceability", 0.0, 1.0, (0.0, 1.0), 0.01, help="0.0 is the least danceable, 1.0 is the most danceable.")
valence_range = st.sidebar.slider("Valence (Happiness)", 0.0, 1.0, (0.0, 1.0), 0.01, help="0.0 sounds sad/depressing, 1.0 sounds happy/cheerful.")
popularity_range = st.sidebar.slider("Popularity", 0, 100, (0, 100), 1, help="0 is unknown, 100 is a global hit.")

st.title("🎧 Spotify Analyzer Statistics")
st.markdown("Search tracks, filter by audio features, and visualize data.")

with st.form("main_search_form", border=False):
    col1, col2 = st.columns(2)
    artist_search = col1.text_input("Search Artist", placeholder="Eminem")
    track_search = col2.text_input("Search Song", placeholder="Lose Yourself")
    main_search_button = st.form_submit_button("🔍")

with st.sidebar.form("search_form", border=False):
    sidebar_search_button = st.form_submit_button("🔍")

if main_search_button or sidebar_search_button:
    base_params = {
        "min_energy": energy_range[0],
        "max_energy": energy_range[1],
        "min_danceability": danceability_range[0],
        "max_danceability": danceability_range[1],
        "min_valence": valence_range[0],
        "max_valence": valence_range[1],
        "min_popularity": popularity_range[0],
        "max_popularity": popularity_range[1],
    }
    
    if selected_genre != "All":
        base_params["genre"] = selected_genre
    if artist_search:
        base_params["artist"] = artist_search
    if track_search:
        base_params["track_name"] = track_search

    with st.spinner("Fetching tracks from database..."):
        fetch_and_update_data(base_params, 0)
        
        st.toast(f" {st.session_state['total_tracks']} tracks found! Click 'X' to close.")

# RESULTS, PAGINATION and CHARTS   
if 'search_results' in st.session_state and not st.session_state['search_results'].empty:
    df = st.session_state['search_results'].copy()
    
    st.subheader("Results")
    
    current_offset = st.session_state['offset']
    df.index = range(current_offset, current_offset + len(df))
    
    display_columns = ['track_name', 'artist', 'genre', 'album_name']
    display_df = df[display_columns].copy()

    display_df = display_df.rename(columns={
        'track_name': 'Song',
        'artist': 'Artist',
        'genre': 'Genre',
        'album_name': 'Album'
    })
    
    row_height = 35
    header_height = 38
    estimated_height = (10 * row_height) + header_height 
    
    st.dataframe(display_df, width='stretch', height=estimated_height)
    
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.session_state['offset'] > 0:
            if st.button("« Prev", key="prev_btn"):
                fetch_and_update_data(st.session_state['search_params'], st.session_state['offset'] - 10)
                st.rerun()
                
    with col_page:
        current_page = (st.session_state['offset'] // 10) + 1
        total_pages = (st.session_state['total_tracks'] // 10) + (1 if st.session_state['total_tracks'] % 10 > 0 else 0)
        st.markdown(f"<div style='text-align: center; margin-top: 10px; font-weight: bold;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)
        
    with col_next:
        if st.session_state['offset'] + 10 < st.session_state['total_tracks']:
            if st.button("Next »", key="next_btn"):
                fetch_and_update_data(st.session_state['search_params'], st.session_state['offset'] + 10)
                st.rerun()

    st.markdown("---")
    st.subheader("🎧 Track Explorer & Audio DNA")
    st.markdown("Select a track to listen and analyze its unique audio features.")
    
    if "track_id" in df.columns:
        track_options = df['track_id'].tolist()
        format_func = lambda x: df.loc[df['track_id'] == x, 'track_name'].values[0] + " - " + df.loc[df['track_id'] == x, 'artist'].values[0]
        
        selected_track_id = st.selectbox("Choose a track", track_options, format_func=format_func, key="track_selector_dropdown")
        
        if selected_track_id:
            detail_res = requests.get(f"{API_BASE_URL}/tracks/{selected_track_id}")
            
            if detail_res.status_code == 200:
                details = detail_res.json()
                
                col_left, col_right = st.columns([1, 2])
                
                with col_left:
                    st.markdown("### Listen Now", )
                    spotify_embed_url = f"https://open.spotify.com/embed/track/{selected_track_id}?utm_source=generator&theme=0"
                    st.components.v1.iframe(spotify_embed_url, width=320, height=80)
                    
                    st.markdown("<br>", unsafe_allow_html=True) 
                    st.metric("Tempo", f"{details.get('tempo', 0):.1f} BPM")
                    st.metric("Popularity", f"{details.get('popularity', 0)} / 100")
                
                with col_right:
                    st.markdown("### Audio DNA")
                    features = ['energy', 'danceability', 'valence', 'acousticness', 'liveness']
                    values = [details.get(feat, 0) for feat in features]
                    
                    df_radar = pd.DataFrame(dict(r=values, theta=[f.capitalize() for f in features]))
                    
                    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', line_color='#1DB954', marker=dict(size=8)) 
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        margin=dict(l=40, r=40, t=20, b=20) 
                    )
                    st.plotly_chart(fig, width='stretch')
                    
    else:
        st.info("Note: To see track details, add 'track_id' to your backend /api/search endpoint SELECT statement.")