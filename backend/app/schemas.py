from pydantic import BaseModel
from typing import Optional, List

# 1. Input Cold Start (Giữ nguyên)
class UserColdStart(BaseModel):
    industry: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    min_salary: Optional[int] = 0
    age: Optional[int] = 22

# 2. Input Lịch sử xem (Giữ nguyên)
class UserHistory(BaseModel):
    viewed_job_ids: List[int]

# 3. Search Request (Giữ nguyên)
class SearchRequest(BaseModel):
    query: str
    model_name: str = "ensemble"
    search_type: str = "title"
    filters: Optional[UserColdStart] = None

# ==========================================
# CẤU TRÚC OUTPUT MỚI (Tách Summarry & Detail)
# ==========================================

# Base: Chứa các trường chung gọn nhẹ (Dùng cho danh sách)
class JobCardSummary(BaseModel):
    id: int
    title: str
    location: str = "Unknown"
    type: str = "Unknown"
    position: str = ""       
    salary_range: str = "Thỏa thuận"
    specializations: List[str] = [] 
    similarity_score: float = 0.0

    class Config:
        from_attributes = True

# Detail: Kế thừa Base + Thêm các trường nội dung dài (Dùng cho trang chi tiết)
class JobCardDetail(JobCardSummary):
    description: str = ""
    requirements: str = ""
    benefit: str = ""       
    experience: str = ""
    level: str = ""