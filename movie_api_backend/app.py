import os
import requests # New import
import pandas as pd
import joblib
import ast
from flask import Flask, request, jsonify
from flask_cors import CORS
from thefuzz import process
from surprise import SVD # Ensure surprise is imported if you use its objects

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# --- TMDb API Setup (NEW) ---
# IMPORTANT: Get your free API key from themoviedb.org and paste it here
# Best practice is to use environment variables, but this will work for now.
TMDB_API_KEY = "eb9efcc4ccf40f0dcb7c3df4e4407369"

def fetch_poster(movie_title):
    """Helper function to fetch a movie poster URL from TMDb."""
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
        response = requests.get(url)
        response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)
        data = response.json()
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException as e:
        print(f"API request error for {movie_title}: {e}")
    except Exception as e:
        print(f"Error fetching poster for {movie_title}: {e}")
    return None # Return None if no poster is found or an error occurs


# --- Load Models and Data (MODIFIED with Relative Paths) ---
try:
    # Models for content-based recommendations
    similarity = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_model.pkl')
    movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/full_movie_data.pkl')
    recommend_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_data.pkl')
    
    # Models for collaborative filtering
    collab_model = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_model.pkl')
    collab_movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_movies.pkl')
    collab_ratings_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_ratings.pkl')
    
    # Lists for fuzzy matching
    all_movie_titles = recommend_df['title'].tolist()
    all_actors = set()
    for cast_list_str in movies_df['cast']:
        cast_list = ast.literal_eval(cast_list_str)
        for actor in cast_list:
            all_actors.add(actor['name'])
    all_actor_names = list(all_actors)

    print("All models, data, and helper lists loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}. Make sure all .pkl files are in the same directory as app.py.")
    # Initialize all to None or empty to prevent app crash on startup
    similarity, movies_df, recommend_df, collab_model, collab_movies_df, collab_ratings_df, all_movie_titles, all_actor_names = (None,) * 8


# --- API Endpoints ---
@app.route('/')
def index():
    return "Movie Recommendation API is running!"

@app.route('/popular-movies', methods=['GET'])
def popular_movies():
    """NEW endpoint to get popular movies for the frontend banner."""
    try:
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = []
        for movie in data.get('results', [])[:15]: # Get top 15 popular movies
             if movie.get('poster_path'):
                results.append({
                    'title': movie.get('title'),
                    'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}"
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_recommendations_with_posters(titles):
    """Helper function to fetch posters for a list of titles."""
    results = []
    for title in titles:
        results.append({
            "title": title,
            "poster_path": fetch_poster(title)
        })
    return results

@app.route('/recommend', methods=['GET'])
def recommend():
    movie_title_query = request.args.get('title')
    if not movie_title_query:
        return jsonify({"error": "A 'title' query parameter is required."}), 400

    best_match = process.extractOne(movie_title_query, all_movie_titles, score_cutoff=75)
    if not best_match:
        return jsonify({"error": f"Movie '{movie_title_query}' not found. No close match."}), 404

    matched_title = best_match[0]
    movie_index = recommend_df[recommend_df['title'] == matched_title].index[0]
    
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_titles = [recommend_df.iloc[i[0]].title for i in movies_list]
    
    # MODIFIED: Fetch posters and return structured data
    recommendations = get_recommendations_with_posters(recommended_titles)
    return jsonify({"recommendations": recommendations})

@app.route('/actor-movies', methods=['GET'])
def get_actor_movies():
    actor_name_query = request.args.get('name')
    if not actor_name_query:
        return jsonify({"error": "An 'name' query parameter is required."}), 400

    best_match = process.extractOne(actor_name_query, all_actor_names, score_cutoff=80)
    if not best_match:
        return jsonify({"error": f"Actor '{actor_name_query}' not found. No close match."}), 404

    matched_actor_name = best_match[0].lower()
    actor_movies = []
    for index, row in movies_df.iterrows():
        cast_list = ast.literal_eval(row['cast'])
        actor_names_in_movie = [actor['name'].lower() for actor in cast_list]
        if matched_actor_name in actor_names_in_movie:
            actor_movies.append(row)
    
    if not actor_movies:
         return jsonify({"error": f"Movies for actor '{best_match[0]}' not found."}), 404

    top_movies_df = pd.DataFrame(actor_movies).sort_values('vote_average', ascending=False).head(5)
    
    # MODIFIED: Fetch posters
    recommendations = get_recommendations_with_posters(top_movies_df['title'].tolist())
    return jsonify({"recommendations": recommendations})

@app.route('/genre-movies', methods=['GET'])
def get_genre_movies():
    genre_name = request.args.get('genre')
    if not genre_name:
        return jsonify({"error": "A 'genre' query parameter is required."}), 400

    genre_name_lower = genre_name.lower()
    genre_movies = []
    for index, row in movies_df.iterrows():
        genres_list = ast.literal_eval(row['genres'])
        genre_names = [genre['name'].lower() for genre in genres_list]
        if genre_name_lower in genre_names:
            genre_movies.append(row)

    if not genre_movies:
        return jsonify({"error": f"Genre '{genre_name}' not found."}), 404
        
    top_movies_df = pd.DataFrame(genre_movies)
    min_votes = top_movies_df['vote_count'].quantile(0.70)
    top_movies_df = top_movies_df[top_movies_df['vote_count'] >= min_votes]
    top_movies_df = top_movies_df.sort_values('vote_average', ascending=False).head(5)
    
    # MODIFIED: Fetch posters
    recommendations = get_recommendations_with_posters(top_movies_df['title'].tolist())
    return jsonify({"recommendations": recommendations})

@app.route('/collaborative-recommend', methods=['GET'])
def collaborative_recommend():
    user_id_str = request.args.get('userId')
    if not user_id_str:
        return jsonify({"error": "A 'userId' query parameter is required."}), 400

    try:
        user_id = int(user_id_str)
        if user_id not in collab_ratings_df['userId'].unique():
             return jsonify({"error": f"User ID {user_id} not found."}), 404
    except ValueError:
        return jsonify({"error": "User ID must be an integer."}), 400
    
    all_movie_ids = collab_ratings_df['movieId'].unique()
    rated_movie_ids = collab_ratings_df[collab_ratings_df['userId'] == user_id]['movieId'].unique()
    unrated_movie_ids = [mid for mid in all_movie_ids if mid not in rated_movie_ids]
    
    predictions = [collab_model.predict(user_id, movie_id) for movie_id in unrated_movie_ids]
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    top_preds = predictions[:5]
    top_movie_ids = [pred.iid for pred in top_preds]
    top_movie_titles = collab_movies_df[collab_movies_df['movieId'].isin(top_movie_ids)]['title'].tolist()
    
    # MODIFIED: Fetch posters
    recommendations = get_recommendations_with_posters(top_movie_titles)
    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    app.run(debug=True, port=5000)