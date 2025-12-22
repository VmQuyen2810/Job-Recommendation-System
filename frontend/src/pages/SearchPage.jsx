import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios'; // [MỚI] Import axios
import { api } from '../api';
import JobCard from '../components/JobCard';
import SearchBar from '../components/SearchBar';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const initialQuery = searchParams.get('q') || '';
  const initialModel = searchParams.get('model') || 'ensemble';

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // [MỚI] State chứa danh sách địa điểm động
  const [locations, setLocations] = useState([]);

  const [query, setQuery] = useState(initialQuery);
  const [modelName, setModelName] = useState(initialModel);
  const [searchType, setSearchType] = useState('overall');
  const [filters, setFilters] = useState({
    min_salary: 0,
    location: '',
    job_type: '',
  });

  const salaryPresets = [
    { label: "Tất cả", value: 0 },
    { label: "> 10 Tr", value: 10 },
    { label: "> 20 Tr", value: 20 },
    { label: "> 30 Tr", value: 30 },
  ];

  // [MỚI] Load danh sách địa điểm từ Backend
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/meta/cold-start-options')
      .then(res => {
        if (res.data.locations) {
          setLocations(res.data.locations);
        }
      })
      .catch(err => console.error("Lỗi tải địa điểm:", err));
  }, []);

  const performSearch = async () => {
    setLoading(true);
    try {
      const payload = {
        query: query,
        model_name: modelName,
        search_type: searchType,
        filters: {
          // Nếu chọn "Tất cả" thì gửi null hoặc chuỗi rỗng
          location: filters.location === "Tất cả" ? null : filters.location,
          job_type: filters.job_type === "Tất cả" ? null : filters.job_type,
          min_salary: Number(filters.min_salary),
        }
      };
      const res = await api.search(payload);
      setJobs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); 

  const handleSearchBtn = () => {
    setSearchParams({ q: query, model: modelName });
    performSearch();
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
    <div className="container dashboard-layout" style={{paddingTop: '20px'}}>
      {/* --- SIDEBAR BỘ LỌC --- */}
      <div className="sidebar">
        <h2 className="section-title" style={{marginTop:0}}>Bộ lọc</h2>
        
        <div className="filter-section">
          <label className="form-label">Địa điểm</label>
          <select className="input-control" 
            value={filters.location} onChange={(e) => setFilters({...filters, location: e.target.value})}>
            <option value="">Tất cả</option>
            {/* [MỚI] Render danh sách địa điểm động */}
            {locations.length > 0 ? (
                locations.map((loc, idx) => (
                    <option key={idx} value={loc}>{loc}</option>
                ))
            ) : (
                // Fallback trong khi chờ load
                <>
                    <option value="Hồ Chí Minh">Hồ Chí Minh</option>
                    <option value="Hà Nội">Hà Nội</option>
                </>
            )}
          </select>
        </div>

        <div className="filter-section">
            <label className="form-label">Hình thức</label>
            <select className="input-control"
              value={filters.job_type} onChange={(e) => setFilters({...filters, job_type: e.target.value})}>
                <option value="">Tất cả</option>
                <option value="Toàn thời gian">Toàn thời gian</option>
                <option value="Bán thời gian">Bán thời gian</option>
                <option value="Thực tập">Thực tập</option>
            </select>
        </div>

        <div className="filter-section">
            <label className="form-label">Lương tối thiểu</label>
            <div className="salary-presets">
              {salaryPresets.map((preset) => (
                <div key={preset.value}
                  className={`salary-chip ${Number(filters.min_salary) === preset.value ? 'active' : ''}`}
                  onClick={() => setFilters({...filters, min_salary: preset.value})}
                >
                  {preset.label}
                </div>
              ))}
            </div>
            <div className="range-wrapper">
               <input type="range" min="0" max="50" step="1"
                 value={filters.min_salary} onChange={(e) => setFilters({...filters, min_salary: e.target.value})} />
               <div className="range-display">{filters.min_salary > 0 ? `Trên ${filters.min_salary} Triệu` : 'Không yêu cầu'}</div>
            </div>
        </div>

        <button onClick={handleSearchBtn} className="btn btn-primary" style={{width: '100%', marginTop: '16px'}}>
            Áp dụng lọc
        </button>
        
        <button onClick={() => navigate('/dashboard')} className="btn" style={{width: '100%', marginTop: '8px', background:'transparent', color: '#64748b'}}>
            ← Về trang chủ
        </button>
      </div>

      {/* --- KẾT QUẢ TÌM KIẾM --- */}
      <div style={{flex: 1}}>
        <div style={{marginBottom: '20px'}}>
           <SearchBar 
              query={query} 
              setQuery={setQuery} 
              modelName={modelName} 
              setModelName={setModelName}
              searchType={searchType}
              setSearchType={setSearchType}
              onSearch={handleSearchBtn} 
           />
        </div>

        <h3 className="section-title">
          Kết quả tìm kiếm ({jobs.length}) 
          {loading && <span style={{marginLeft:'10px', fontSize:'0.9rem', color:'var(--primary-color)'}}>⏳ Đang tìm...</span>}
        </h3>
        
        <div>
          {jobs.map(job => (
            <JobCard key={job.id} job={job} onClick={() => handleJobClick(job.id)} />
          ))}
          {!loading && jobs.length === 0 && (
            <div style={{textAlign:'center', padding:'40px', color:'#64748b'}}>
              <p style={{fontSize:'1.2rem', fontWeight:'bold'}}>Không tìm thấy kết quả nào.</p>
              <p>Hãy thử thay đổi từ khóa hoặc bộ lọc.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}