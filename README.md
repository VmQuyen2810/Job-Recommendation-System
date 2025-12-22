# Job Recommendation System

Dự án Hệ thống gợi ý việc làm thông minh sử dụng các kỹ thuật NLP (BERT, TF-IDF, LaBSE) để phân tích và gợi ý công việc phù hợp nhất dựa trên hồ sơ và hành vi tìm kiếm của người dùng.

## 🛠 Công nghệ sử dụng

* **Frontend:** ReactJS, Vite, Axios
* **Backend:** Python, FastAPI
* **AI/ML:** PyTorch, Scikit-learn, Pandas, NumPy
* **Models:** BGE-M3, LaBSE, Paraphrase Multilingual

---

## 📥 Hướng dẫn Cài đặt & Chạy dự án

Vui lòng làm theo từng bước dưới đây để khởi chạy hệ thống.

### Bước 1: Clone dự án về máy


### Bước 2: Tải Model & Dữ liệu (BẮT BUỘC)

Tải xuống tại đây: [👉 https://drive.google.com/drive/u/0/folders/1Gsocn79wuHQZEx_3mntlhludGReoP4SA 👈]

Giải nén file vừa tải.

Copy toàn bộ các thư mục model và file .pkl vào Thư mục gốc của dự án (ngang hàng với folder backend và frontend).

### Bước 3: Cài đặt môi trường ảo với requirements.txt

Run backend:

cd backend
uvicorn app.main:app --reload

Run frontend:

cd frontend
npm run dev
