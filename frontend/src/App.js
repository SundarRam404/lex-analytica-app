// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [files, setFiles] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [mainAnalysis, setMainAnalysis] = useState('');
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [score, setScore] = useState('');
  const [justification, setJustification] = useState('');
  const [openAccordion, setOpenAccordion] = useState(null);

  const handleReset = () => {
    setFiles(null);
    setError('');
    setMainAnalysis('');
    setTimelineEvents([]);
    setScore('');
    setJustification('');
    setOpenAccordion(null);
  };

  const parseAnalysis = (text) => {
    const timelineRegex = /### 3\. Case Timeline([\s\S]*?)### 4\./;
    const timelineMatch = text.match(timelineRegex);
    let restOfText = text;

    if (timelineMatch) {
      const timelineBlock = timelineMatch[1];
      restOfText = text.replace(timelineRegex, '### 4.');
      const eventRegex = /- \*\*(.*?):\*\* (.*?)\n\s+- \*\*Details:\*\* ([\s\S]*?)(?=\n- \*\*|\n###|$)/g;
      const events = [];
      let match;
      while ((match = eventRegex.exec(timelineBlock)) !== null) {
        events.push({ date: match[1], title: match[2], details: match[3].trim() });
      }
      setTimelineEvents(events);
    }
    
    const scoreRegex = /Argument Strength Score:[\s\S]*?SCORE:\s*(\d+\/\d+)\n([\s\S]*)/;
    const scoreMatch = restOfText.match(scoreRegex);
    if (scoreMatch) {
      setScore(scoreMatch[1]);
      setJustification(scoreMatch[2].trim());
      restOfText = restOfText.replace(scoreRegex, '');
    }

    // --- THIS IS THE FIX for the trailing ** ---
    const cleanedText = restOfText.trim().replace(/\s*\*\*$/, '');
    setMainAnalysis(cleanedText);
  };

  const handleAnalyzeClick = async () => {
    if (!files) return;
    setIsLoading(true);
    handleReset();
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) { formData.append('files', files[i]); }
    try {
      const apiUrl = `${process.env.REACT_APP_API_URL}/analyze-pdf/`;
const response = await axios.post(apiUrl, formData);
      parseAnalysis(response.data.analysis);
    } catch (err) {
      setError(err.response ? err.response.data.detail : 'Backend server error.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const toggleAccordion = (index) => setOpenAccordion(openAccordion === index ? null : index);
  const handleFileChange = (e) => { setFiles(e.target.files); setError(''); };
  const handleBrowseClick = () => { document.getElementById('file-input').click(); };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container"><span>⚖️</span><h1>AutoCase Pro</h1></div>
        <p className="tagline">Complete Legal Document Analysis Pipeline</p>
      </header>
      <main className="main-content">
        {isLoading ? (
          <div className="loader-container"><img src="/loader.gif" alt="Analyzing..." /><p>Analyzing...</p></div>
        ) : mainAnalysis ? (
          <div className="results-container">
            <h2>Analysis Complete</h2>
            {score && (
              <div className="score-container">
                <h3>Argument Strength Score</h3>
                <div className="score-display">{score}</div>
                <p className="score-justification">{justification}</p>
              </div>
            )}
            {timelineEvents.length > 0 && (
              <div className="timeline-container">
                <h3>Case Timeline</h3>
                {timelineEvents.map((event, index) => (
                  <div key={index} className="timeline-item">
                    <div className="timeline-header" onClick={() => toggleAccordion(index)}>
                      <span><strong>{event.date}:</strong> {event.title}</span>
                      <button className="toggle-btn">{openAccordion === index ? '−' : '+'}</button>
                    </div>
                    {openAccordion === index && (<div className="timeline-details"><p>{event.details}</p></div>)}
                  </div>
                ))}
              </div>
            )}
            <div className="results-text-wrapper">
              <div className="results-text">
                <ReactMarkdown>{mainAnalysis}</ReactMarkdown>
              </div>
            </div>
            <button className="analyze-button" onClick={handleReset}>Analyze Another Document</button>
          </div>
        ) : (
          <div className="upload-container">
            <h2>Upload Legal Documents</h2>
            <div className="drop-zone" onClick={handleBrowseClick}>
              {files ? (
                <div className="file-list"><h4>Selected:</h4><p>{files.length} file(s)</p></div>
              ) : (
                <>
                  <span className="upload-icon">↑</span><h3>Upload Documents</h3><p>Drag & drop or click to browse.</p>
                </>
              )}
              <input type="file" id="file-input" multiple hidden onChange={handleFileChange}/>
            </div>
            {error && <p className="error-message">{error}</p>}
            <button className="analyze-button" onClick={handleAnalyzeClick} disabled={!files}>Analyze Case</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;