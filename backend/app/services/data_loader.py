import pandas as pd
import numpy as np
from app.config import settings
import sys
# Import hàm tính điểm heuristic
from app.services.heuristic import calculate_score_ranking

class DataLoader:
    def __init__(self):
        print("🔄 Đang khởi tạo DataLoader...")
        try:
            print(f"📂 Đang đọc file dữ liệu từ: {settings.DATA_PATH}")
            self.df = pd.read_excel(settings.DATA_PATH, engine='openpyxl')
            
            # Pre-process cơ bản
            self.df['min_salary_edited'] = self.df['min_salary_edited'].fillna(0).astype(int)
            self.df['max_salary_edited'] = self.df['max_salary_edited'].fillna(0).astype(int)
            self.df['location'] = self.df['location'].fillna("Unknown").astype(str)
            self.df['type'] = self.df['type'].fillna("Unknown").astype(str)
            
            # Đảm bảo có cột description và title_processed
            if 'description' not in self.df.columns:
                 self.df['description'] = ""
            if 'title_processed' not in self.df.columns:
                 self.df['title_processed'] = self.df['title']

            if 'id' not in self.df.columns:
                self.df['id'] = self.df.index

            print(f"✅ Đã tải xong {len(self.df)} dòng dữ liệu!")
            
        except FileNotFoundError:
            print(f"❌ LỖI: Không tìm thấy file tại {settings.DATA_PATH}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ LỖI DATA: {str(e)}")
            sys.exit(1)

    def cold_start_filter(self, criteria):
        """
        Cold Start Heuristic:
        Thay vì filter cứng, ta tính điểm % phù hợp (0-100) cho từng job.
        """
        # 1. Chuyển criteria (Pydantic model) sang dict để dễ xử lý
        profile = {
            'industry': criteria.industry,
            'location': criteria.location,
            'job_type': criteria.job_type,
            'age': criteria.age if criteria.age else 22
        }

        # 2. Lọc cứng sơ bộ (Pre-filter) để tăng tốc (Optional)
        # Chỉ giữ lại những job có lương phù hợp hoặc không yêu cầu lương
        # Nếu criteria.min_salary > 0, loại bỏ những job lương quá thấp (nhưng cẩn thận job 'Thỏa thuận' = 0)
        candidates = self.df.copy()
        if criteria.min_salary > 0:
            # Giữ lại job có lương >= mong muốn HOẶC lương = 0 (Thỏa thuận)
            candidates = candidates[
                (candidates['max_salary_edited'] >= criteria.min_salary) | 
                (candidates['max_salary_edited'] == 0)
            ]

        # Nếu lọc xong mà hết data thì lấy lại toàn bộ
        if candidates.empty:
            candidates = self.df.copy()

        # 3. Tính điểm Heuristic cho từng dòng (Apply)
        # Hàm calculate_heuristic_score nhận vào (row, profile)
        scores = candidates.apply(lambda row: calculate_heuristic_score(row, profile), axis=1)

        # 4. Gán điểm vào DataFrame và Sort
        candidates['similarity_score'] = scores
        
        # Lấy Top job có điểm cao nhất (ví dụ > 0)
        # Sắp xếp giảm dần theo điểm
        top_candidates = candidates.sort_values(by='similarity_score', ascending=False)
        
        return top_candidates

data_loader = DataLoader()