import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ColdStart from './pages/ColdStart';
import Dashboard from './pages/Dashboard';
import SearchPage from './pages/SearchPage'; // Trang mới
import JobDetail from './pages/JobDetail';
import './App.css';
import './Components.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<ColdStart />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/search" element={<SearchPage />} /> {/* Route Mới */}
          <Route path="/job/:id" element={<JobDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;