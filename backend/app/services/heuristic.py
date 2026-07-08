import re
import pandas as pd

# 1. TỪ ĐIỂN MAP NGÀNH NGHỀ
INDUSTRY_KEYWORDS = {
    "Công nghệ thông tin": ["developer", "lập trình", "phần mềm", "software", "it", "cntt", "system", "mạng", "data", "tester", "erp", "website", "mobile", "react", "java", "net", "php", "backend", "frontend"],
    "Kinh doanh / Bán hàng": ["sale", "kinh doanh", "bán hàng", "thị trường", "tư vấn", "telesale", "account"],
    "Marketing / Truyền thông": ["marketing", "seo", "content", "truyền thông", "media", "digital", "quảng cáo", "biên tập", "brand"],
    "Hành chính / Nhân sự": ["nhân sự", "hr", "hành chính", "tuyển dụng", "admin", "văn phòng", "lễ tân", "thư ký"],
    "Kế toán / Tài chính": ["kế toán", "kiểm toán", "tài chính", "thu ngân", "finance", "audit", "accountant"],
    "Cơ khí / Kỹ thuật": ["cơ khí", "kỹ thuật", "điện", "bảo trì", "vận hành", "kỹ sư", "thiết kế máy"],
    "Dịch vụ / Khách hàng": ["cskh", "khách hàng", "phục vụ", "bảo vệ", "tạp vụ", "chăm sóc"],
}

def normalize(text):
    if not isinstance(text, str): return ""
    return text.lower().strip()

# [QUAN TRỌNG] Hàm lọc chung cho cả Search và Cold Start
def cold_start_filter(df, filters):
    """
    Lọc DataFrame dựa trên tiêu chí: Location, Industry, Job Type, Min Salary.
    """
    filtered_df = df.copy()
    
    # 1. Lọc Địa điểm
    loc = filters.get('location')
    if loc and loc != "Tất cả":
        loc_norm = normalize(loc)
        filtered_df = filtered_df[filtered_df['location'].str.lower().str.contains(loc_norm, na=False)]

    # 2. Lọc Ngành nghề (Dùng từ điển đồng nghĩa)
    ind = filters.get('industry')
    if ind and ind in INDUSTRY_KEYWORDS:
        keywords = INDUSTRY_KEYWORDS[ind]
        pattern = '|'.join([re.escape(k) for k in keywords])
        
        mask_title = filtered_df['title'].str.lower().str.contains(pattern, na=False, regex=True)
        if 'specializations' in filtered_df.columns:
            mask_spec = filtered_df['specializations'].str.lower().str.contains(pattern, na=False, regex=True)
            filtered_df = filtered_df[mask_title | mask_spec]
        else:
            filtered_df = filtered_df[mask_title]

    # 3. Lọc Hình thức
    job_type = filters.get('job_type')
    if job_type and job_type != "Tất cả":
        type_norm = normalize(job_type)
        filtered_df = filtered_df[filtered_df['type'].str.lower().str.contains(type_norm, na=False)]

    # 4. [MỚI] Lọc Lương (Min Salary)
    # Giữ lại job có Max Salary >= Mức user chọn
    min_salary = filters.get('min_salary', 0)
    if min_salary and float(min_salary) > 0:
        filtered_df = filtered_df[filtered_df['max_salary_edited'] >= float(min_salary)]

    return filtered_df

# Hàm tính điểm (Giữ nguyên)
def calculate_score_ranking(row, profile):
    score = 0.0
    title = normalize(row.get('title', ''))
    position = normalize(row.get('position', ''))
    age = profile.get('age', 22)
    
    if age < 22:
        if any(k in title or k in position for k in ['thực tập', 'intern', 'part-time', 'sinh viên']): score += 50
    elif 22 <= age <= 24:
        if any(k in title or k in position for k in ['fresher', 'junior', 'nhân viên', 'mới']): score += 30
        if "senior" not in title and "trưởng" not in title: score += 20
    elif 25 <= age <= 29:
        if any(k in title or k in position for k in ['senior', 'chuyên viên', 'leader']): score += 50
    else:
        if any(k in title or k in position for k in ['manager', 'trưởng', 'giám đốc']): score += 50

    return score