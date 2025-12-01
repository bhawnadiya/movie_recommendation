import pickle
import requests
import streamlit as st
import zipfile
import io


# ---------------------------------------
# DOWNLOAD & LOAD PKL FROM GITHUB ZIP
# ---------------------------------------
def load_pkl_from_github_zip(zip_url, pkl_name):
    response = requests.get(zip_url, timeout=30)
    if response.status_code != 200:
        raise Exception("❌ Failed to download ZIP file")

    z = zipfile.ZipFile(io.BytesIO(response.content))

    if pkl_name not in z.namelist():
        raise Exception(f"❌ {pkl_name} not found inside ZIP")

    with z.open(pkl_name) as f:
        return pickle.load(f)


# ---------------------------------------
# LOAD FILES
# ---------------------------------------
similarity = load_pkl_from_github_zip(
    "https://github.com/bhawnadiya/movie_recommendation/releases/download/v1.0/similarity.zip",
    "similarity.pkl"
)

movies = load_pkl_from_github_zip(
    "https://github.com/bhawnadiya/movie_recommendation/releases/download/v1.0/movie_list.zip",
    "movie_list.pkl"
)

FALLBACK_POSTER = "https://via.placeholder.com/500x750?text=No+Image"


# ---------------------------------------
# FETCH POSTER
# ---------------------------------------
def fetch_poster(movie_id):
    api_key = "c85bd5e138da982cb0357638dafa815a"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        data = requests.get(url, timeout=10).json()
        path = data.get("poster_path")

        if path and isinstance(path, str) and path.strip() != "":
            return "https://image.tmdb.org/t/p/w500/" + path
        else:
            return FALLBACK_POSTER

    except:
        return FALLBACK_POSTER


# ---------------------------------------
# RECOMMEND MOVIES
# ---------------------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1],
    )

    names = []
    posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)

        # FINAL SAFETY CHECK
        if not poster or poster.strip() == "":
            poster = FALLBACK_POSTER

        posters.append(poster)
        names.append(movies.iloc[i[0]].title)

    return names, posters


# ---------------------------------------
# STREAMLIT UI
# ---------------------------------------
st.header("🎬 Movie Recommender System")

movie_list = movies["title"].values
selected_movie = st.selectbox("Choose a movie", movie_list)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    # DEBUG LOG — SEE POSTERS IN TERMINAL
    print("\n=== POSTERS RETURNED ===")
    for p in posters:
        print(p)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i], use_column_width=True)
