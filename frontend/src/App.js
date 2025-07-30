// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

// --- Legal Facts for the "Fun Stuff" Section ---
const legalFacts = [
  "In ancient Athens, citizens could vote to exile a politician for 10 years by writing their name on a piece of pottery, a process called 'ostracism'.",
  "The smallest court in the world is the Court of Peculiars in the UK, which historically handled ecclesiastical law in specific parishes.",
  "The term 'jaywalking' was originally coined in the 1920s by the auto industry to shame pedestrians for walking in the street.",
  "In the 19th century, a case in the US argued whether a tomato was a fruit or a vegetable for tax purposes. The Supreme Court ruled it a vegetable. (Nix v. Hedden, 1893)",
  "The longest-serving Chief Justice of the United States was John Marshall, who served for 34 years from 1801 to 1835."
];

function App() {
  const [files, setFiles] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [mainAnalysis, setMainAnalysis] = useState('');
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [score, setScore] = useState('');
  const [justification, setJustification] = useState('');
  const [openAccordion, setOpenAccordion] = useState(null);
  const [factOfTheDay, setFactOfTheDay] = useState('');

  useEffect(() => {
    // Pick a random fact when the app loads
    setFactOfTheDay(legalFacts[Math.floor(Math.random() * legalFacts.length)]);
  }, []);

  // All your functions (handleReset, parseAnalysis, etc.) remain the same
  const handleReset = () => {
    setFiles(null); setError(''); setMainAnalysis(''); setTimelineEvents([]);
    setScore(''); setJustification(''); setOpenAccordion(null);
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

  // --- Main Render Logic ---
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-container"><span>⚖️</span><h1>Verdicto-AI</h1></div>
          <p className="tagline">Decoding Judgments with Precision</p>
          <p className="credit">Engineered by Sundar Ram</p>
        </div>
      </header>
      
      <main className="main-content">
        {isLoading ? (
          <div className="loader-container"><img src="/loader.gif" alt="Analyzing..." /><p>Analyzing...</p></div>
        ) : mainAnalysis ? (
          // --- RESULTS VIEW ---
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
            <div className="results-text-wrapper"><ReactMarkdown className="results-text">{mainAnalysis}</ReactMarkdown></div>
            <button className="analyze-button" onClick={handleReset}>Analyze Another Document</button>
          </div>
        ) : (
          // --- LANDING PAGE VIEW ---
          <div className="landing-page">
            <div className="upload-container">
              <h2>Upload Legal Documents for Analysis</h2>
              <div className="drop-zone" onClick={handleBrowseClick}>
                {files ? (
                  <div className="file-list"><h4>Selected:</h4><p>{files.length} file(s)</p></div>
                ) : (
                  <>
                    <span className="upload-icon">↑</span><h3>Upload Legal Documents</h3><p>Drag & drop or click to browse.</p>
                  </>
                )}
                <input type="file" id="file-input" multiple hidden onChange={handleFileChange}/>
              </div>
              {error && <p className="error-message">{error}</p>}
              <button className="analyze-button" onClick={handleAnalyzeClick} disabled={!files}>Analyze Case</button>
            </div>

            <section className="page-section">
              <h2 className="section-title">Harnessing AI for Unmatched Legal Insight</h2>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>🏛️ Case Metadata</h4>
                  <p>Instantly extract titles, citations, judges, and parties involved.</p>
                </div>
                <div className="feature-card">
                  <h4>📈 Critical Analysis</h4>
                  <p>Identify core legal arguments, counter-arguments, and precedent analysis.</p>
                </div>
                <div className="feature-card">
                  <h4>🗓️ Interactive Timeline</h4>
                  <p>Generate a complete, interactive chronology of case events with detailed descriptions.</p>
                </div>
                <div className="feature-card">
                  <h4>🎓 Study & Moot Prep</h4>
                  <p>Get auto-generated viva questions and answers to prepare for exams and moot courts.</p>
                </div>
              </div>
            </section>

            <section className="page-section fun-fact-section">
              <h2 className="section-title">Legal Fact of the Day</h2>
              <p className="fun-fact-text">"{factOfTheDay}"</p>
            </section>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>⚖️ Verdicto-AI &copy; 2025</p>
      </footer>
    </div>
  );
}

export default App;
