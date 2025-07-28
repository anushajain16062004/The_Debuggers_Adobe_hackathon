import React, { useState } from 'react';
import axios from 'axios';

function Analyzer() {
  const [files, setFiles] = useState([]);
  const [collection, setCollection] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [collections, setCollections] = useState([]);

  const fetchCollections = async () => {
    const response = await axios.get('/api/collections');
    setCollections(response.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (collection) {
      formData.append('collection', collection);
    }

    try {
      const response = await axios.post('/api/analyze', formData);
      setResults(response.data);
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Analysis failed. Please check console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analyzer-container">
      <h2>PDF Analyzer</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Collection:
            <select 
              value={collection} 
              onChange={(e) => setCollection(e.target.value)}
              onFocus={fetchCollections}
            >
              <option value="">None</option>
              {collections.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </label>
        </div>
        
        <div>
          <label>
            Upload PDFs:
            <input 
              type="file" 
              multiple 
              accept=".pdf"
              onChange={(e) => setFiles([...e.target.files])}
            />
          </label>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {results && (
        <div className="results">
          <h3>Analysis Results</h3>
          <div className="sections">
            {results.sections.map((section, index) => (
              <div key={index} className={`section ${section.is_uploaded ? 'uploaded' : ''}`}>
                <h4>{section.text}</h4>
                <p>Document: {section.document} | Page: {section.page}</p>
                <p>Importance: {section.importance}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Analyzer;