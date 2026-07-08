import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import JobCard from '../components/JobCard';

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null); 
  const [similarJobs, setSimilarJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    
    // 1. Gọi API Chi tiết
    api.getJobDetail(id)
      .then(res => {
        setJob(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Lỗi lấy chi tiết job:", err);
        setLoading(false);
      });

    // 2. Gọi API Tương đồng
    api.getSimilar(id)
      .then(res => setSimilarJobs(res.data))
      .catch(console.error);
      
  }, [id]);

  const handleJobClick = (jobId) => {
     const history = JSON.parse(localStorage.getItem('viewed_jobs') || '[]');
     if (!history.includes(jobId)) {
         history.push(jobId);
         localStorage.setItem('viewed_jobs', JSON.stringify(history));
     }
     navigate(`/job/${jobId}`);
     window.scrollTo(0, 0);
  };

  if (loading) return <div className="loading-container">⏳ Đang tải thông tin...</div>;
  if (!job) return <div className="error-msg">❌ Không tìm thấy công việc (ID: {id})</div>;

  return (
    <div className="container">
      <button onClick={() => navigate(-1)} className="btn btn-back">← Quay lại danh sách</button>
      
      <div className="detail-layout">
        {/* CỘT TRÁI: Nội dung chi tiết */}
        <div>
          <div className="job-header-card">
             <h1 className="header-title">{job.title}</h1>
             
             <div className="tags-container">
                <span className="tag-badge tag-location">📍 {job.location}</span>
                {/* [SỬA] Đổi salary_str thành salary_range */}
                <span className="tag-badge tag-salary">💰 {job.salary_range}</span>
                <span className="tag-badge tag-type">⏰ {job.type}</span>
                {job.position && <span className="tag-badge tag-pos">🎓 {job.position}</span>}
             </div>

             {job.specializations && job.specializations.length > 0 && (
               <div style={{marginTop: '20px'}}>
                  {job.specializations.map((tag, idx) => (
                    <span key={idx} className="skill-chip">{tag}</span>
                  ))}
               </div>
             )}
          </div>

          <div className="content-card">
             <section>
                <h3 className="section-title">Mô tả công việc</h3>
                {/* Sử dụng pre-line để giữ xuống dòng từ backend */}
                <div className="text-content" style={{whiteSpace: 'pre-line'}}>
                    {job.description || "Chưa có mô tả chi tiết."}
                </div>
             </section>

             {job.requirements && (
               <section>
                  <h3 className="section-title">Yêu cầu ứng viên</h3>
                  <div className="text-content" style={{whiteSpace: 'pre-line'}}>
                      {job.requirements}
                  </div>
               </section>
             )}

             {job.benefit && (
               <section>
                  <h3 className="section-title">Quyền lợi</h3>
                  <div className="text-content" style={{whiteSpace: 'pre-line'}}>
                      {job.benefit}
                  </div>
               </section>
             )}
          </div>
        </div>

        {/* CỘT PHẢI: Gợi ý tương tự */}
        <div>
           <h3 className="similar-jobs-title">🧩 Việc làm tương tự</h3>
           <div>
              {similarJobs.length === 0 ? <p style={{color:'#64748b'}}>Không có gợi ý.</p> : (
                  similarJobs.map(simJob => (
                      <JobCard key={simJob.id} job={simJob} onClick={() => handleJobClick(simJob.id)} />
                  ))
              )}
           </div>
        </div>
      </div>
    </div>
  );
}