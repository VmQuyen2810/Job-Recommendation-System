import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export const api = {
    // 1. Cold Start
    coldStart: (criteria) => axios.post(`${API_URL}/cold-start`, criteria),

    // 2. Search (có hỗ trợ filters)
    search: (payload) => axios.post(`${API_URL}/search`, payload),

    // 3. User Recommendation (Dựa trên lịch sử)
    recommend: (viewedIds) => axios.post(`${API_URL}/recommend`, { viewed_job_ids: viewedIds }),

    // 4. Similar Jobs (Dựa trên ID job hiện tại)
    getSimilar: (jobId) => axios.get(`${API_URL}/job/${jobId}/similar`),

    //5. Get Job Detail (Mới)
    getJobDetail: (jobId) => axios.get(`${API_URL}/job/${jobId}`),
};