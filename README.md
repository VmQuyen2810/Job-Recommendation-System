# Job Recommendation System

Dự án Hệ thống gợi ý việc làm thông minh sử dụng các kỹ thuật NLP để phân tích và gợi ý công việc phù hợp nhất dựa trên hồ sơ và hành vi tìm kiếm của người dùng.


## Hướng dẫn Cài đặt & Chạy dự án

### Bước 1: Clone dự án về máy

### Bước 2: Tải Model & Dữ liệu (BẮT BUỘC)

Tải xuống tại đây: [👉 https://drive.google.com/drive/u/0/folders/1Gsocn79wuHQZEx_3mntlhludGReoP4SA 👈]

Giải nén file vừa tải.

Copy toàn bộ các thư mục model và file .pkl vào Thư mục gốc của dự án (ngang hàng với folder backend và frontend).
Cấu trúc:
```text
MY-PROJECT/
├── backend/               # Mã nguồn Backend
├── frontend/              # Mã nguồn Frontend
├── data/                  # Thư mục chứa data Excel (nếu có)
│
├── bge_m3_model_vn_basic/         <-- 📂 
├── bge_m3_model_vn_upgrade/       <-- 📂 
├── labse_model_vn_basic/          <-- 📂 
├── labse_model_vn_upgrade/        <-- 📂 
├── word2vec_.../                  <-- 📂 
│
├── tfidf_matrix_basic.pkl         <-- 📄 
├── tfidf_matrix_upgrade.pkl       <-- 📄
├── ... (các file .pkl, .bin khác)
│
├── .gitignore
└── README.md
```

### Bước 3: Cài đặt môi trường ảo với requirements.txt

Run backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Run frontend:
```bash
cd frontend
npm run dev
```
