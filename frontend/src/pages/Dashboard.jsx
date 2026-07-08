import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api';
import JobCard from '../components/JobCard';
import SkeletonJobCard from '../components/SkeletonJobCard';
import SearchBar from '../components/SearchBar'; 
import axios from 'axios';

export default function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const hasInitialData = location.state?.initialJobs && location.state.initialJobs.length > 0;
  const [recommendedJobs, setRecommendedJobs] = useState(hasInitialData ? location.state.initialJobs : []);
  const [loading, setLoading] = useState(!hasInitialData);
  
  // State SearchBar
  const [query, setQuery] = useState('');
  const [modelName, setModelName] = useState('ensemble');
  // [MỚI] Thêm state này nếu muốn Dashboard cũng chọn được Title/Overall
  const [searchType, setSearchType] = useState('overall'); 
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/meta/cold-start-options')
      .then(res => setLocations(res.data.locations || []))
      .catch(console.error);
    if (!hasInitialData) {
      const history = JSON.parse(localStorage.getItem('viewed_jobs') || '[]');
      api.recommend(history)
        .then(res => {
          setRecommendedJobs(res.data);
          setLoading(false);
        })
        .catch(err => setLoading(false));
    } else {
        window.history.replaceState({}, document.title);
    }
  }, [hasInitialData]);

  const handleSearch = () => {
    if (!query.trim()) return;
    // Truyền cả searchType sang trang search
    navigate(`/search?q=${encodeURIComponent(query)}&model=${modelName}&type=${searchType}`);
  };

  const handleJobClick = (id) => {
    const history = JSON.parse(localStorage.getItem('viewed_jobs') || '[]');
    if (!history.includes(id)) {
      history.push(id);
      localStorage.setItem('viewed_jobs', JSON.stringify(history));
    }
    navigate(`/job/${id}`);
  };

  return (
    <div className="container" style={{paddingTop: '40px'}}>
      
      {/* 1. THANH TÌM KIẾM FIT CỨNG */}
      <div className="modern-search-wrapper">
        <h1 style={{textAlign: 'center', color:'#1e293b', fontWeight:'800', marginBottom:'24px', fontSize:'2rem'}}>
           Tìm công việc phù hợp
        </h1>
        
        {/* Component SearchBar tái sử dụng */}
        <SearchBar 
            query={query} 
            setQuery={setQuery} 
            modelName={modelName} 
            setModelName={setModelName}
            searchType={searchType}       // Truyền prop
            setSearchType={setSearchType} // Truyền prop
            onSearch={handleSearch} 
        />
      </div>

      {/* 2. GỢI Ý */}
      <div>
        <h2 className="section-title" style={{fontSize: '1.4rem', marginBottom: '24px', display:'flex', alignItems:'center', gap:'10px'}}>
           Gợi ý dành cho bạn
           {hasInitialData && <span style={{fontSize:'0.8rem', background:'#dbeafe', color:'#1e40af', padding:'4px 10px', borderRadius:'20px', fontWeight:'600'}}></span>}
        </h2>
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px'}}>
          {loading ? Array(6).fill(0).map((_, i) => <SkeletonJobCard key={i} />) : 
             recommendedJobs.map(job => (
                <JobCard key={job.id} job={job} onClick={() => handleJobClick(job.id)} highlight />
             ))
          }
        </div>
      </div>
    </div>
  );
}