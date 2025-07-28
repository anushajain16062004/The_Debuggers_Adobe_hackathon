import React, { useState } from 'react';
import KnowledgeGraph from './components/KnowledgeGraph';
import './styles.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeCollection = async (collection) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ collection })
      });
      setResults(await response.json());
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>PDF Knowledge Connect</h1>
      <div className="controls">
        <button onClick={() => analyzeCollection('travel_planning')}>
          Analyze Travel Docs
        </button>
        <button onClick={() => analyzeCollection('acrobat_learning')}>
          Analyze HR Docs
        </button>
        <button onClick={() => analyzeCollection('recipe_collection')}>
          Analyze Recipes
        </button>
      </div>
      
      {loading && <div className="loader">Analyzing...</div>}
      
      {results && (
        <div className="results">
          <KnowledgeGraph data={results} />
          <div className="sections">
            <h2>Key Sections</h2>
            {results.sections.map((section, i) => (
              <div key={i} className="section-card">
                <h3>{section.text}</h3>
                <p>Document: {section.document} | Page: {section.page}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;