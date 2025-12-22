import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

export default function ColdStart() {
  const navigate = useNavigate();
  
  // State chứa options từ Backend
  const [options, setOptions] = useState({
      locations: [],
      industries: []
  });

  const [formData, setFormData] = useState({
    industry: '', 
    location: '',
    job_type: 'Toàn thời gian',
    age: 22,
    min_salary: 0
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // [MỚI] Gọi API lấy danh sách Ngành nghề & Địa điểm khi vào trang
  useEffect(() => {
    // Lưu ý: Đảm bảo URL này khớp với port backend của bạn (thường là 8000)
    fetch('http://127.0.0.1:8000/api/meta/cold-start-options')
      .then(res => res.json())
      .then(data => {
         setOptions(data);
         // Set default
         setFormData(prev => ({
             ...prev,
             industry: data.industries?.[0] || "Công nghệ thông tin",
             location: "Hồ Chí Minh"
         }));
      })
      .catch(err => {
         console.error("Lỗi lấy metadata, dùng fallback:", err);
         setOptions({
             industries: ["Công nghệ thông tin", "Kinh doanh / Bán hàng", "Marketing / Truyền thông", "Kế toán / Tài chính"],
             locations: ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Bình Dương"]
         });
         setFormData(prev => ({ ...prev, industry: "Công nghệ thông tin", location: "Hồ Chí Minh" }));
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await api.coldStart(formData);
      navigate('/dashboard', { state: { initialJobs: res.data } });
    } catch (err) {
      console.error(err);
      alert("Không thể lấy dữ liệu gợi ý. Vui lòng kiểm tra lại Server Backend.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="cold-start-page">
      <div className="cold-start-card">
        <div style={{textAlign: 'center', marginBottom: '30px'}}>
           <h1 style={{fontSize: '2.2rem', fontWeight: '800', color: '#1e293b', marginBottom: '10px'}}>Chào mừng bạn! 🚀</h1>
           <p style={{color: '#64748b', fontSize: '1.1rem'}}>Cho chúng tôi biết vài thông tin để gợi ý việc làm phù hợp nhất.</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          
          {/* NGÀNH NGHỀ */}
          <div className="form-group">
            <label className="form-label">Ngành nghề quan tâm</label>
            <select className="input-control" 
                value={formData.industry} 
                onChange={e => setFormData({...formData, industry: e.target.value})}>
                {options.industries.map((ind, idx) => (
                    <option key={idx} value={ind}>{ind}</option>
                ))}
            </select>
          </div>

          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}} className="form-group">
            {/* THÀNH PHỐ */}
            <div>
              <label className="form-label">Thành phố</label>
              <select className="input-control" 
                value={formData.location} onChange={e => setFormData({...formData, location: e.target.value})}>
                <option value="Tất cả">Tất cả</option>
                {options.locations.map((loc, idx) => (
                    <option key={idx} value={loc}>{loc}</option>
                ))}
              </select>
            </div>
            
            {/* TUỔI */}
            <div>
              <label className="form-label">Tuổi</label>
              <input type="number" className="input-control" 
                value={formData.age} onChange={e => setFormData({...formData, age: Number(e.target.value)})} />
            </div>
          </div>

          <div className="form-group">
             <label className="form-label">Loại hình</label>
             <select className="input-control"
                value={formData.job_type} onChange={e => setFormData({...formData, job_type: e.target.value})}>
                <option>Toàn thời gian</option>
                <option>Bán thời gian</option>
                <option>Thực tập</option>
             </select>
          </div>

          <button type="submit" className="btn btn-primary" disabled={isSubmitting} 
            style={{marginTop: '20px', padding: '14px', fontSize: '1.1rem', width: '100%', borderRadius: '10px'}}>
            {isSubmitting ? 'Đang xử lý...' : 'Bắt đầu khám phá'}
          </button>
        </form>
      </div>
    </div>
  );
}