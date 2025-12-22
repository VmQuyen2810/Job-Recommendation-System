from fastapi import APIRouter, HTTPException
from typing import List, Union
import pandas as pd
import numpy as np
import re

# Import schema
from app.schemas import JobCardSummary, JobCardDetail, SearchRequest, UserColdStart, UserHistory
from app.services.data_loader import data_loader
from app.services.search_engine import search_engine
from app.services.heuristic import INDUSTRY_KEYWORDS, cold_start_filter, calculate_score_ranking

router = APIRouter()

# --- 1. HÀM XỬ LÝ LƯƠNG ---
def format_salary(row):
    s_str = str(row.get('salary_range', '')).strip()
    # Nếu salary_range rỗng hoặc là các giá trị rác -> Tự tính toán
    if not s_str or s_str.lower() in ['nan', 'none', '', '0', 'thỏa thuận']:
        try:
            min_s = float(row.get('min_salary_edited', 0))
            max_s = float(row.get('max_salary_edited', 0))
            
            if min_s == 0 and max_s == 0: return "Thỏa thuận"
            if min_s > 0 and max_s == 0: return f"Trên {int(min_s)} Triệu"
            if min_s == 0 and max_s > 0: return f"Lên tới {int(max_s)} Triệu"
            return f"{int(min_s)} - {int(max_s)} Triệu"
        except:
            return "Thỏa thuận"
    return s_str

# --- 2. HELPER CHUYỂN ĐỔI DATAFRAME -> SCHEMA ---
def df_to_job_cards(df: pd.DataFrame, full_details: bool = False) -> List[Union[JobCardSummary, JobCardDetail]]:
    results = []
    
    # Giá trị mặc định để tránh lỗi NoneType
    fill_values = {
        "location": "Unknown", "type": "Unknown", "position": "", "specializations": ""
    }
    if full_details:
        fill_values.update({
            "description": "", "requirements": "", "benefits": "", "experience": "", "level": ""
        })

    df_clean = df.fillna(fill_values)

    for idx, row in df_clean.iterrows():
        # Ưu tiên lấy điểm match_score (từ cold start) hoặc similarity_score (từ search)
        score = row.get("similarity_score", row.get("match_score", 0.0))
        job_id = row.get('id', idx)

        # Xử lý list chuyên môn
        specs_raw = row.get('specializations', [])
        specs_list = []
        if isinstance(specs_raw, str):
            specs_list = [s.strip() for s in specs_raw.split(',') if s.strip()]
        elif isinstance(specs_raw, list):
            specs_list = specs_raw

        job_data = {
            "id": int(job_id),
            "title": str(row.get('title', row.get('title_processed', 'No Title'))),
            "location": str(row.get('location', 'Unknown')),
            "type": str(row.get('type', 'Unknown')),
            "position": str(row.get('position', '')),
            "salary_range": format_salary(row), 
            "specializations": specs_list,
            "similarity_score": float(score)
        }

        if full_details:
            job_data.update({
                "description": str(row.get('description', '')),
                "requirements": str(row.get('requirements', '')),
                "benefit": str(row.get('benefits', row.get('benefit', ''))),
                "experience": str(row.get('experience', '')),
                "level": str(row.get('level', ''))
            })
            results.append(JobCardDetail(**job_data))
        else:
            results.append(JobCardSummary(**job_data))

    return results

# ==================== API ENDPOINTS ====================

# 1. API Lấy danh sách Metadata (Đã sửa lỗi location bị gộp)
@router.get("/meta/cold-start-options")
def get_options():
    try:
        # A. Xử lý Location
        raw_locs = data_loader.df['location'].dropna().astype(str).tolist()
        loc_set = set()
        
        for item in raw_locs:
            # 1. Fix lỗi HTML entity
            clean_item = item.replace("&amp;", "&")
            
            # 2. Tách "Hà Nội & 5 nơi khác" -> Lấy "Hà Nội"
            if "&" in clean_item:
                clean_item = clean_item.split("&")[0]
            
            # 3. Tách "Hà Nội, Hồ Chí Minh" -> Lấy tỉnh đầu tiên
            primary_loc = clean_item.split(',')[0].strip()
            
            if primary_loc and len(primary_loc) < 50:
                loc_set.add(primary_loc)
        
        clean_locs = sorted(list(loc_set))
        
        # B. Lấy list Ngành nghề từ Dictionary
        industries = list(INDUSTRY_KEYWORDS.keys())
        
        return {
            "locations": clean_locs,
            "industries": industries,
            "types": ["Toàn thời gian", "Bán thời gian", "Thực tập", "Remote"]
        }
    except Exception as e:
        print(f"Error meta: {e}")
        return {"locations": [], "industries": [], "types": []}

# 2. API Cold Start (Gợi ý ban đầu)
@router.post("/cold-start", response_model=List[JobCardSummary])
def cold_start_endpoint(criteria: UserColdStart):
    try:
        filters_dict = criteria.dict() 

        # Bước 1: Lọc cứng (Dùng hàm chung)
        df_filtered = cold_start_filter(data_loader.df, filters_dict)
        
        if df_filtered.empty:
            return []
            
        # Bước 2: Tính điểm Heuristic (Xếp hạng theo cấp bậc/tuổi)
        df_filtered['match_score'] = df_filtered.apply(
            lambda row: calculate_score_ranking(row, filters_dict), axis=1
        )
        
        # Bước 3: Sort và lấy Top 20
        top_jobs = df_filtered.sort_values(by='match_score', ascending=False).head(20)
        
        return df_to_job_cards(top_jobs, full_details=False)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# 3. API Search Jobs (Đã tích hợp Bộ lọc bên trái)
@router.post("/search", response_model=List[JobCardSummary])
def search_jobs(request: SearchRequest):
    try:
        # A. Bắt đầu với toàn bộ dữ liệu
        df_candidate = data_loader.df

        # B. ÁP DỤNG BỘ LỌC (QUAN TRỌNG: Đã thêm logic này)
        if request.filters:
            filters_dict = request.filters.dict()
            # Dùng chung hàm lọc của Cold Start để đảm bảo nhất quán
            # Hàm này sẽ lọc theo Location, Industry, Job Type và Min Salary
            df_candidate = cold_start_filter(df_candidate, filters_dict)

        # Nếu lọc xong mà rỗng -> Trả về rỗng ngay
        if df_candidate.empty: 
            return []

        query = request.query.strip()
        
        # C. Trường hợp User chỉ lọc mà KHÔNG nhập từ khóa
        if not query:
            return df_to_job_cards(df_candidate.head(20), full_details=False)

        # D. Trường hợp User CÓ nhập từ khóa -> Gọi AI Search trên tập đã lọc
        df_result = search_engine.search(
            query=query, 
            df_jobs=df_candidate, # <-- Chỉ search trong tập dữ liệu đã lọc sạch
            model_name=request.model_name, 
            search_field=request.search_type, 
            top_k=20
        )

        return df_to_job_cards(df_result, full_details=False)
        
    except Exception as e:
        print(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 4. API Chi tiết Job
@router.get("/job/{job_id}", response_model=JobCardDetail)
def get_job_detail(job_id: int):
    if job_id not in data_loader.df.index: 
        raise HTTPException(status_code=404, detail="Job Not Found")
    # Lấy row dưới dạng DataFrame để dùng chung hàm convert
    row = data_loader.df.loc[[job_id]]
    return df_to_job_cards(row, full_details=True)[0]

# 5. API Recommend (Dựa trên lịch sử xem)
@router.post("/recommend", response_model=List[JobCardSummary])
def recommend_for_user(history: UserHistory):
    try:
        if not history.viewed_job_ids:
            # Nếu chưa có lịch sử, trả về random
            return df_to_job_cards(data_loader.df.sample(20), full_details=False)
            
        df_res = search_engine.get_user_recommendation(history.viewed_job_ids, data_loader.df, top_k=20)
        return df_to_job_cards(df_res, full_details=False)
    except Exception as e:
        print(f"Error recommend: {e}")
        return []

# 6. API Similar Jobs (Job tương tự)
@router.get("/job/{job_id}/similar", response_model=List[JobCardSummary])
def recommend_similar(job_id: int):
    try:
        if job_id not in data_loader.df.index: 
            raise HTTPException(status_code=404, detail="Job Not Found")
            
        job_row = data_loader.df.loc[job_id]
        # Ghép title + description ngắn để tìm kiếm
        content = str(job_row['title']) + " " + str(job_row['description'])[:200]
        
        df_res = search_engine.get_recommendation_ensemble(
            content, data_loader.df, top_k=10, exclude_id=job_id
        )
        return df_to_job_cards(df_res, full_details=False)
    except Exception as e:
        print(f"Error similar: {e}")
        return []