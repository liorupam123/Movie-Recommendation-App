import React, { useState } from 'react';
import PosterMarquee from './PosterMarquee'; // Import the new component
import './App.css';

const genres = [
  "Action", "Adventure", "Animation", "Comedy", "Crime", 
  "Documentary", "Drama", "Family", "Fantasy", "History",
  "Horror", "Music", "Mystery", "Romance", "Science Fiction",
  "TV Movie", "Thriller", "War", "Western"
];

function App() {
  const [searchType, setSearchType] = useState('movie');
  const [query, setQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFetch = async () => {
    // For genre, if the user hasn't selected a valid genre, don't fetch.
    if (searchType === 'genre' && !query) {
        setError("Please select a genre.");
        return;
    }
    if (!query.trim() && searchType !== 'genre') return;

    setIsLoading(true);
    setError(null);
    setRecommendations([]);

    let apiUrl = '';
    if (searchType === 'movie') {
      apiUrl = `http://127.0.0.1:5000/recommend?title=${encodeURIComponent(query)}`;
    } else if (searchType === 'actor') {
      apiUrl = `http://127.0.0.1:5000/actor-movies?name=${encodeURIComponent(query)}`;
    } else if (searchType === 'genre') {
      apiUrl = `http://127.0.0.1:5000/genre-movies?genre=${encodeURIComponent(query)}`;
    } else if (searchType === 'user') {
      apiUrl = `http://127.0.0.1:5000/collaborative-recommend?userId=${encodeURIComponent(query)}`;
    }

    try {
      const response = await fetch(apiUrl);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Server error.');
      }
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleFetch();
    }
  };
  
  const renderInputField = () => {
    if (searchType === 'genre') {
      return (
        <select value={query} onChange={(e) => setQuery(e.target.value)} className="movie-input">
          <option value="">-- Select a Genre --</option>
          {genres.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
      );
    }
    
    let placeholder = 'Enter a movie title...';
    if (searchType === 'actor') placeholder = "Enter an actor's name...";
    if (searchType === 'user') placeholder = "Enter a User ID (e.g., 1 to 610)...";
    
    return (
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        className="movie-input"
      />
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        
        <PosterMarquee /> {/* The animated poster banner */}

        <h1>🎬 Movie Recommendation Engine</h1>
        <p>Discover your next favorite movie!</p>
        
        <div className="search-options">
          <label><input type="radio" value="movie" checked={searchType === 'movie'} onChange={(e) => {setQuery(''); setSearchType(e.target.value)}} /> By Movie</label>
          <label><input type="radio" value="actor" checked={searchType === 'actor'} onChange={(e) => {setQuery(''); setSearchType(e.target.value)}} /> By Actor</label>
          <label><input type="radio" value="genre" checked={searchType === 'genre'} onChange={(e) => {setQuery(''); setSearchType(e.target.value)}} /> By Genre</label>
          <label><input type="radio" value="user" checked={searchType === 'user'} onChange={(e) => {setQuery(''); setSearchType(e.target.value)}} /> For You (User ID)</label>
        </div>

        <div className="input-container">
          {renderInputField()}
          <button onClick={handleFetch} disabled={isLoading} className="recommend-button">
            {isLoading ? 'Searching...' : 'Get Recommendations'}
          </button>
        </div>

        <div className="results-container">
          {error && <p className="error-message">{error}</p>}
          
          {/* Updated results display with posters */}
          {recommendations.length > 0 && (
            <div className="recommendations-grid">
              {recommendations.map((movie, index) => (
                <div key={`${movie.title}-${index}`} className="movie-result-card">
                  {movie.poster_path ? (
                    <img src={movie.poster_path} alt={movie.title} />
                  ) : (
                    <div className="no-poster">No Poster Available</div>
                  )}
                  <h3>{movie.title}</h3>
                </div>
              ))}
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;