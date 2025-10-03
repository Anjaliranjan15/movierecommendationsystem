import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=3,  # Retry up to 3 times
                backoff_factor=1,  # Wait 1s, 2s, 4s between retries
                status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
                raise_on_status=False)
session.mount("https://", HTTPAdapter(max_retries=retries))

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = session.get(url, timeout=10)  # Set timeout to avoid hanging
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        data = response.json()
        
        # Check if poster_path exists
        if 'poster_path' not in data or data['poster_path'] is None:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"  # Fallback image
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Error"  # Fallback image for errors

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
            time.sleep(0.25)  # Add a 250ms delay to avoid hitting rate limits
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

st.header('Movie Recommender System')
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    if recommended_movie_names:  # Only display if recommendations exist
        col1, col2, col3, col4, col5 = st.columns(5)  # Updated to st.columns (st.beta_columns is deprecated)
        with col1:
            st.text(recommended_movie_names[0])
            st.image(recommended_movie_posters[0])
        with col2:
            st.text(recommended_movie_names[1])
            st.image(recommended_movie_posters[1])
        with col3:
            st.text(recommended_movie_names[2])
            st.image(recommended_movie_posters[2])
        with col4:
            st.text(recommended_movie_names[3])
            st.image(recommended_movie_posters[3])
        with col5:
            st.text(recommended_movie_names[4])
            st.image(recommended_movie_posters[4])
    else:
        st.warning("No recommendations available due to an error.")