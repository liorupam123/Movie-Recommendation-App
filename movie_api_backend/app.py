import pandas as pd
import joblib
import ast
from flask import Flask, request, jsonify
from flask_cors import CORS
from thefuzz import process # NEW: Import the fuzzy matching tool

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# --- Load Models and Data ---
try:
    # Model for "recommend by movie"
    similarity = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_model.pkl')
    # Data for all features
    movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/full_movie_data.pkl')
    # Data for "recommend by movie" (needs the 'title' and 'tags' structure)
    recommend_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_data.pkl')
    
    collab_model = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_model.pkl')
    collab_movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_movies.pkl')
    collab_ratings_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_ratings.pkl')
    print("Collaborative filtering model loaded.")

    # NEW: Create a list of all movie titles for fuzzy matching
    all_movie_titles = recommend_df['title'].tolist()
    
    # NEW: Create a master list of all unique actor names for fuzzy matching
    all_actors = set()
    for cast_list_str in movies_df['cast']:
        cast_list = ast.literal_eval(cast_list_str)
        for actor in cast_list:
            all_actors.add(actor['name'])
    all_actor_names = list(all_actors)

    print("Models, data, and helper lists created successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    similarity, movies_df, recommend_df = None, None, None
    collab_model, collab_movies_df, collab_ratings_df = None, None, None
    all_movie_titles, all_actor_names = [], []

# --- Helper function ---
def parse_list(text):
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []

# --- API Endpoints ---
@app.route('/')
def index():
    return "Movie Recommendation API is running!"

# ENDPOINT 1: By Movie Title (MODIFIED with Fuzzy Matching)
@app.route('/recommend', methods=['GET'])
def recommend():
    movie_title_query = request.args.get('title')
    if not movie_title_query:
        return jsonify({"error": "A 'title' query parameter is required."}), 400

    # NEW: Find the best match for the user's query from our list of titles
    best_match = process.extractOne(movie_title_query, all_movie_titles, score_cutoff=75)
    
    if not best_match:
        return jsonify({"error": f"Movie '{movie_title_query}' not found. No close match."}), 404

    # Use the best matched title to proceed
    matched_title = best_match[0]
    movie_index = recommend_df[recommend_df['title'] == matched_title].index[0]
    
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = [recommend_df.iloc[i[0]].title for i in movies_list]
    return jsonify({"recommendations": recommended_movies})

# ENDPOINT 2: By Actor (MODIFIED with Fuzzy Matching)
@app.route('/actor-movies', methods=['GET'])
def get_actor_movies():
    actor_name_query = request.args.get('name')
    if not actor_name_query:
        return jsonify({"error": "An 'name' query parameter is required."}), 400

    # NEW: Find the best matching actor name from our master list
    best_match = process.extractOne(actor_name_query, all_actor_names, score_cutoff=80)
    
    if not best_match:
        return jsonify({"error": f"Actor '{actor_name_query}' not found. No close match."}), 404

    # Use the best matched actor name to find movies
    matched_actor_name = best_match[0].lower()
    actor_movies = []
    for index, row in movies_df.iterrows():
        cast_list = parse_list(row['cast'])
        actor_names_in_movie = [actor['name'].lower() for actor in cast_list]
        if matched_actor_name in actor_names_in_movie:
            actor_movies.append(row)
    
    if not actor_movies:
         return jsonify({"error": f"Movies for actor '{best_match[0]}' not found."}), 404

    top_movies_df = pd.DataFrame(actor_movies).sort_values('vote_average', ascending=False).head(5)
    return jsonify({"recommendations": top_movies_df['title'].tolist()})


# ENDPOINT 3: By Genre (No changes needed)
@app.route('/genre-movies', methods=['GET'])
def get_genre_movies():
    genre_name = request.args.get('genre')
    if not genre_name:
        return jsonify({"error": "A 'genre' query parameter is required."}), 400

    genre_name_lower = genre_name.lower()
    genre_movies = []
    for index, row in movies_df.iterrows():
        genres_list = parse_list(row['genres'])
        genre_names = [genre['name'].lower() for genre in genres_list]
        if genre_name_lower in genre_names:
            genre_movies.append(row)

    if not genre_movies:
        return jsonify({"error": f"Genre '{genre_name}' not found."}), 404
        
    top_movies_df = pd.DataFrame(genre_movies)
    min_votes = top_movies_df['vote_count'].quantile(0.70)
    top_movies_df = top_movies_df[top_movies_df['vote_count'] >= min_votes]
    top_movies_df = top_movies_df.sort_values('vote_average', ascending=False).head(5)
    
    return jsonify({"recommendations": top_movies_df['title'].tolist()})

# ENDPOINT 4: Get personalized recommendations for a user ID (NEW)
@app.route('/collaborative-recommend', methods=['GET'])
def collaborative_recommend():
    user_id_str = request.args.get('userId')
    if not user_id_str:
        return jsonify({"error": "A 'userId' query parameter is required."}), 400

    try:
        user_id = int(user_id_str)
        # Check if user exists
        if user_id not in collab_ratings_df['userId'].unique():
             return jsonify({"error": f"User ID {user_id} not found."}), 404
    except ValueError:
        return jsonify({"error": "User ID must be an integer."}), 400
    
    # Get all movie IDs
    all_movie_ids = collab_ratings_df['movieId'].unique()
    # Get movie IDs the user has already rated
    rated_movie_ids = collab_ratings_df[collab_ratings_df['userId'] == user_id]['movieId'].unique()
    # Get movies to predict
    unrated_movie_ids = [mid for mid in all_movie_ids if mid not in rated_movie_ids]
    
    # Predict ratings for unrated movies
    predictions = [collab_model.predict(user_id, movie_id) for movie_id in unrated_movie_ids]
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    # Get top 5 recommendations
    top_preds = predictions[:5]
    top_movie_ids = [pred.iid for pred in top_preds]
    top_movie_titles = collab_movies_df[collab_movies_df['movieId'].isin(top_movie_ids)]['title'].tolist()
    
    return jsonify({"recommendations": top_movie_titles})

if __name__ == '__main__':
    app.run(debug=True, port=5000)