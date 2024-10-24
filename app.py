import streamlit as st
import pandas as pd
import pickle
import requests
from requests.exceptions import ConnectionError
import time

# Set page layout to wide mode
st.set_page_config(layout="wide")

# Load data
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Fetch movie posters with error handling
def fetch_poster(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=a75c81ea7870baff915eaa44456f7217&language=en-US'
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback poster
    except ConnectionError:
        st.warning("Connection error while fetching posters. Please check your internet connection.")
        return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback for connection issues
    except requests.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as err:
        st.error(f"An error occurred: {err}")
        return "https://via.placeholder.com/500x750?text=No+Image"

# Movie recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# --- Streamlit app structure ---

# Create two columns for layout
left_column, right_column = st.columns([2, 1])  # Adjust ratio as needed

# --- Left Column: Title, Subtitle, and Recommender Bar ---
with left_column:
    st.title('🍿 Movie Recommendation System 🎬')
    st.subheader('Find movies that match your taste!')

    # Recommender bar styling
    st.markdown("""
        <style>
            /* Center the dropdown and button */
            .stSelectbox, .stButton {
                margin: 0 auto;
                display: block;
                width: 20%;
            }

            /* Rounded edges and compact selectbox */
            .stSelectbox div[data-baseweb='select'] {
                background-color: #848484;
                color: #ffffff;
                border-radius: 30px;
                border: 2px solid #848484;
                padding: 10px;
                box-shadow: 0px 4px 12px rgba(60, 60, 60, 0.1);
            }

            /* Style the button like a doodle */
            .stButton button {
                background-color: #C9E4CA;
                color: #3c3c3c;
                font-size: 14px;
                font-family: 'Comic Sans MS', sans-serif;
                border: 3px dashed #C9E4CA;
                border-radius: 30px;
                padding: 6px 15px;
                margin-top: 15px;
                box-shadow: 3px 3px #C9E4CA;
            }

            /* Button hover effect */
            .stButton button:hover {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 3px dashed #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    # Dropdown for movie selection
    selected_movie_name = st.selectbox(
        'Select a movie to get recommendations:',
        movies['title'].values
    )

    # When the recommend button is pressed
    if st.button('Recommend'):
        with st.spinner('Fetching recommendations...'):
            names, posters = recommend(selected_movie_name)

# --- Right Column: Display Recommendations ---
with right_column:
    if 'names' in locals() and 'posters' in locals():  # Check if recommendations exist
        st.write("### Recommended Movies")

        # Display movie recommendations with their posters
        cols1 = st.columns(3)  # First row with 3 columns
        for i in range(3):
            if i < len(names):
                with cols1[i]:
                    if posters[i]:
                        st.image(posters[i], caption=names[i], use_column_width=True)

        cols2 = st.columns(2)  # Second row with 2 columns
        for i in range(3, 5):
            if i < len(names):
                with cols2[i - 3]:
                    if posters[i]:
                        st.image(posters[i], caption=names[i], use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/500x750?text=No+Image", caption=names[i], use_column_width=True)

# --- Greige-themed custom styling (Apply to the whole app) ---
st.markdown("""
    <style>
        body {
            background-color: #F5F5DC;
            color: #3c3c3c;
            font-size: 12px;
        }

        [data-testid="stAppViewContainer"] {
            padding: 0;
            background-color: #F5F5DC;
        }

        h1, h2, h3 {
            font-family: 'Comic Sans MS', 'Arial', sans-serif;
            color: #6a5d4d;
            text-align: left;
            text-transform: uppercase;
            font-size: 18px;
        }

        .block-container {
            padding: 20px;
            background-color: #F5F5DC;
        }
    </style>
""", unsafe_allow_html=True)
