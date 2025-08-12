// Create a new file: src/PosterMarquee.js

import React, { useState, useEffect } from 'react';
import './PosterMarquee.css'; // We will create this CSS file next

const PosterMarquee = () => {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    // Fetch popular movies from our new backend endpoint
    const fetchPopular = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/popular-movies');
        const data = await response.json();
        // Duplicate the list to create a seamless loop effect
        setMovies([...data, ...data]);
      } catch (error) {
        console.error("Failed to fetch popular movies:", error);
      }
    };

    fetchPopular();
  }, []);

  return (
    <div className="marquee-container">
      <div className="marquee-content">
        {movies.map((movie, index) => (
          <div key={index} className="poster-card">
            <img src={movie.poster_path} alt={movie.title} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default PosterMarquee;