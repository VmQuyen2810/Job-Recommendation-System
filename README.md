# SemLex: A Hybrid Semantic-Lexical Framework for Job Recommendation

This intelligent Job Recommendation System utilizes NLP techniques to analyze and suggest the most suitable jobs based on user profiles and search behaviors.

## 📄 Research Paper & Abstract

*(Click on the image below to read the full research paper)*

<a href="https://github.com/user-attachments/files/31168590/Job_Recommendation_System____MAPR2026__Camera_ready_.pdf" target="_blank">
  <img width="514" height="584" alt="Paper Abstract" src="https://github.com/user-attachments/assets/31249915-56ef-4fc6-8ed4-cb4573d3ca22" />
</a>



> [cite_start]**Reference:** "SemLex: A Hybrid Semantic-Lexical Framework for Vietnamese Job Recommendation"[cite: 289, 290].
> 
> [cite_start]**Abstract:** To address the semantic mismatch between candidate queries and job postings, this project proposes SemLex, an intelligent hybrid job recommendation framework[cite: 297]. [cite_start]By combining TF-IDF with BGE-M3 embeddings for lexical-semantic matching[cite: 298], SemLex effectively captures diverse wording and search intents. [cite_start]Experimental results show that the framework consistently outperforms standalone baselines, achieving an NDCG@10 of 0.888 on the manually annotated benchmark[cite: 299].

---

## 🚀 Installation & Usage Guide

### Step 1: Clone the Repository

### Bước 2: Download Models & Data (REQUIRED)

To run the application, you must download the pre-trained models and vectorized matrices:
👉 [Download the required files here](https://drive.google.com/drive/u/0/folders/1Gsocn79wuHQZEx_3mntlhludGReoP4SA) 👈

Once downloaded, extract the archive and copy all the model folders and .pkl files directly into the Root Directory of the project (at the same level as the backend and frontend folders).
Expected Project Structure:
```text
MY-PROJECT/
├── backend/               # Backend source code
├── frontend/              # Frontend source code
├── data/                  # Excel data folder (if any)
│
├── bge_m3_model_vn_basic/         <-- 📂 Extracted model
├── bge_m3_model_vn_upgrade/       <-- 📂 Extracted model
├── labse_model_vn_basic/          <-- 📂 Extracted model
├── labse_model_vn_upgrade/        <-- 📂 Extracted model
├── word2vec_.../                  <-- 📂 Extracted model
│
├── tfidf_matrix_basic.pkl         <-- 📄 Extracted matrix
├── tfidf_matrix_upgrade.pkl       <-- 📄 Extracted matrix
├── ... (other .pkl, .bin files)
│
├── .gitignore
└── README.md
```

### Step 3: Setup Environment & Run the Application
Please open two separate terminals to run the backend and frontend simultaneously.

🖥️ Terminal 1: Run the Backend (FastAPI)
First, set up your Python virtual environment and install the required dependencies.
# Create and activate a virtual environment (optional but recommended)
```
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```
# Install dependencies
```
pip install -r requirements.txt
```
# Navigate to the backend folder and start the server
```
cd backend
uvicorn app.main:app --reload
```

The API server will run at: http://localhost:8000

🌐 Terminal 2: Run the Frontend
Navigate to the frontend directory, install Node.js modules, and start the application.
```
cd frontend
npm install
npm run dev
```
The web interface will typically be available at: http://localhost:3000 or the port specified in your terminal.
