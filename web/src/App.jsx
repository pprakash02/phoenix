import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import StatusBar from './components/StatusBar';
import SetupPage from './pages/SetupPage';
import AnalysisPage from './pages/AnalysisPage';
import ProgressPage from './pages/ProgressPage';
import ReviewPage from './pages/ReviewPage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import { useState } from 'react';
import './App.css';

function AppContent() {
  const [sessionData, setSessionDataState] = useState(() => {
    const saved = localStorage.getItem('phoenix_sessionData');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return null;
      }
    }
    return null;
  });

  const setSessionData = (data) => {
    setSessionDataState(data);
    if (data) {
      localStorage.setItem('phoenix_sessionData', JSON.stringify(data));
    } else {
      localStorage.removeItem('phoenix_sessionData');
    }
  };
  return (
    <div className="app-layout">
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<SetupPage onSessionCreated={setSessionData} />} />
          <Route path="/analysis" element={<AnalysisPage sessionData={sessionData} />} />
          <Route path="/progress" element={<ProgressPage sessionData={sessionData} />} />
          <Route path="/review" element={<ReviewPage sessionData={sessionData} />} />
          <Route path="/results" element={<ResultsPage sessionData={sessionData} />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>
      <StatusBar sessionId={sessionData?.session_id} />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
