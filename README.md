Here's the drive link to for all the .pkl files.
https://drive.google.com/drive/folders/1KiS5PNF-CfTQHDq75rYGjKzYVAOswVUq?usp=drive_link

similarity = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_model.pkl')
movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/full_movie_data.pkl')
recommend_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/movie_data.pkl')
collab_model = joblib.load('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_model.pkl')
collab_movies_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_movies.pkl')
collab_ratings_df = pd.read_pickle('/data1/students/rupam/Self_Project/Movie_Recommendation/movie_api_backend/collaborative_ratings.pkl')
