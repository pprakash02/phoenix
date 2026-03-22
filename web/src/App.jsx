import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import StatusBar from './components/StatusBar';
import SetupPage from './pages/SetupPage';
import AnalysisPage from './pages/AnalysisPage';
import ProgressPage from './pages/ProgressPage';
import ReviewPage from './pages/ReviewPage';
import ResultsPage from './pages/ResultsPage';
import { useState } from 'react';
import './App.css';

function App() {
  const [sessionData, setSessionData] = useState(null);

  return (
    <Router>
      <div className="app-layout">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<SetupPage onSessionCreated={setSessionData} />} />
            <Route path="/analysis" element={<AnalysisPage sessionData={sessionData} />} />
            <Route path="/progress" element={<ProgressPage sessionData={sessionData} />} />
            <Route path="/review" element={<ReviewPage sessionData={sessionData} />} />
            <Route path="/results" element={<ResultsPage sessionData={sessionData} />} />
          </Routes>
        </main>
        <StatusBar sessionId={sessionData?.session_id} />
      </div>
    </Router>
  );
}

export default App;
