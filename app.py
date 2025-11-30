import pickle
import streamlit as st
import requests
import time

from requests.adapters import HTTPAdapter, Retry

# ===============================
#  REQUEST SESSION WITH RETRIES
# ===============================
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


# ===============================
#  LOAD PKL FILE FROM GOOGLE DRIVE
# ===============================
def load_pkl_from_drive(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    return pickle.loads(response.content)


# Load similarity.pkl (176MB file hosted on Drive)
similarity = load_pkl_from_drive("1IfFUDSYgb_x4pRT5z6jzjmd7yujrPM_Y")

# Load movie_list.pkl (from your second Drive link)
movies = load_pkl_from_drive("1xdXiWr3ufitYng_TjkFT1CIUxA0JApNk")


# ===============================
#  FETCH MOVIE POSTERS
# ===============================
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c85bd5e138da982cb0357638dafa815a&language=en-US"
    print(f"Fetching poster for movie_id: {movie_id}")

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "default_image_url_here"

    except requests.exceptions.RequestException as e:
        print(f"Failed for movie ID {movie_id}: {e}")
        return "default_image_url_here"


# ===============================
#  MOVIE RECOMMENDATION LOGIC
# ===============================
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# ===============================
#  STREAMLIT UI
# ===============================
st.header("🎬 Movie Recommender System")

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])
