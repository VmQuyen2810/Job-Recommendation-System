export default function JobCard({ job, onClick, highlight = false }) {
    return (
      <div onClick={onClick} className={`job-card ${highlight ? 'highlight' : ''}`}>
        <div className="card-header">
          <div>
            <h4 className="job-title">{job.title}</h4>
          </div>
          {job.similarity_score > 0 && (
            <span className="bg-green-100 text-green-800 text-xs font-bold px-2 py-1 rounded">
                {job.similarity_score > 1 ? (
                // > 1 → giả sử là phần trăm (0-100), làm tròn và thêm "% Khớp"
                `${Math.round(job.similarity_score)}% Khớp`
                ) : (
                // <= 1 → hiển thị số gốc với nhãn "Độ tương đồng"
                `Độ tương đồng: ${job.similarity_score.toFixed(2)}`
                )}
            </span>
          )}
        </div>
        
        <div className="card-meta">
          <span className="meta-item">📍 {job.location}</span>
          <span className="meta-item">💰 {job.salary_range}</span>
          <span className="meta-item">⏰ {job.type}</span>
        </div>
      </div>
    );
  }