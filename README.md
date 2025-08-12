🎬 Hybrid Movie Recommendation System
A full-stack movie recommendation engine combining Content-Based Filtering and Collaborative Filtering to provide accurate and personalized suggestions.

🚀 Features
Content-Based Filtering using TF-IDF + Cosine Similarity

Collaborative Filtering using Singular Value Decomposition (SVD)

Hybrid Recommendation Mode for balanced results

Fuzzy Search for typo-tolerant movie queries

Dynamic UI with movie posters and details from TMDb API

Full-stack architecture (Flask backend + React.js frontend)

📂 Datasets
TMDb 5000 Movie Dataset – metadata for content-based model

MovieLens Dataset – ratings for collaborative filtering

🛠 Tech Stack
Backend: Python, Flask, scikit-learn, scikit-surprise
Frontend: React.js, HTML5, CSS3
External APIs: TMDb API

📜 How It Works
Preprocess movie metadata and ratings

Generate recommendations via selected model

Serve results through REST API

Display results in a responsive web interface

Here's the complete Project Report:
https://drive.google.com/file/d/1azQXuc87pfS2Gb-lUWSKm4h_jJ0j_-Ti/view?usp=drive_link

Here's the Drive link for all the .pkl files:  
https://drive.google.com/drive/folders/1KiS5PNF-CfTQHDq75rYGjKzYVAOswVUq?usp=drive_link  

| Variable            | File Name                  |
| ------------------- | -------------------------- |
| similarity          | movie\_model.pkl           |
| movies\_df          | full\_movie\_data.pkl      |
| recommend\_df       | movie\_data.pkl            |
| collab\_model       | collaborative\_model.pkl   |
| collab\_movies\_df  | collaborative\_movies.pkl  |
| collab\_ratings\_df | collaborative\_ratings.pkl |
 
