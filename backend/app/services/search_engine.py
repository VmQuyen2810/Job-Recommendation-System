import pandas as pd
import numpy as np
import re
import string
import joblib
import warnings
from underthesea import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from app.config import settings

# Import Gensim an toàn
try:
    from gensim.models import KeyedVectors, Doc2Vec
except ImportError:
    KeyedVectors = None
    Doc2Vec = None


warnings.filterwarnings("ignore")

class SearchEngine:
    def __init__(self):
        self.models = {}       
        self.embeddings = {}   
        self.stopwords = []

        try:
            with open(settings.STOPWORDS_PATH, 'r', encoding='utf-8') as f:
                self.stopwords = f.read().splitlines()
        except:
            self.stopwords = []

    # ------------------ UTILS ------------------
    def preprocess_text(self, text):
        if not text or not isinstance(text, str): return ""
        text = text.lower()
        text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        tokens = word_tokenize(text, format="text").split()
        return " ".join([w for w in tokens if w not in self.stopwords])
    
    def preprocess_tokens(self, text):
        s = self.preprocess_text(text)
        return s.split() if s else []

    def _safe_map_results(self, df_jobs, full_scores, top_k):
        # Lấy index hợp lệ
        valid_indices = [i for i in df_jobs.index if i < len(full_scores)]
        if not valid_indices: return pd.DataFrame()

        subset_scores = full_scores[valid_indices]
        
        df_results = df_jobs.loc[valid_indices].copy()
        df_results['similarity_score'] = subset_scores
        
        # Sắp xếp giảm dần
        return df_results.nlargest(top_k, 'similarity_score')

    def normalize_scores(self, scores):
        """
        Chuẩn hóa điểm số về khoảng [0, 1] để cộng gộp công bằng.
        """
        if len(scores) == 0: return scores
        min_s = np.min(scores)
        max_s = np.max(scores)
        if max_s - min_s == 0: return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

    # =========================================================
    # 1. ENSEMBLE CORE (MÔ HÌNH CHÍNH)
    # =========================================================
    def search_ensemble(self, query, df_jobs, search_field="overall", top_k=20):
        """
        Hàm Search Lai ghép (Weighted Hybrid):
        - 70% BGE-M3 (Semantic)
        - 30% TF-IDF (Keyword)
        """
        query_str = self.preprocess_text(query)
        indices = df_jobs.index


        # --- A. Tính điểm TF-IDF (30%) ---
        try:
            tfidf_key = "tfidf_basic" if search_field == "title" else "tfidf_upgrade"
            self.load_tfidf(tfidf_key)
            
            vec_tfidf = self.models[tfidf_key].transform([query_str])
            # Tính trên toàn bộ DB
            raw_tfidf = cosine_similarity(vec_tfidf, self.embeddings[f"{tfidf_key}_matrix"]).flatten()
            
            # Slice theo tập candidate
            if max(indices) < len(raw_tfidf):
                sub_tfidf = raw_tfidf[indices]
            else:
                sub_tfidf = np.zeros(len(indices))
        except Exception as e:
            print(f"⚠️ Ensemble TF-IDF Error: {e}")
            sub_tfidf = np.zeros(len(indices))

        # --- B. Tính điểm BGE-M3 (70%) ---
        try:
            bge_key = "bge_m3_basic" if search_field == "title" else "bge_m3_upgrade"
            self.load_transformer(bge_key)
            
            vec_bge = self.models[bge_key].encode([query_str], normalize_embeddings=True)
            
            # Chọn embedding matrix
            emb_key = f"{bge_key}_{search_field}"

        
            # print(f"🔍 DEBUG ENSEMBLE:")
            # print(f"   - Mode: {search_field}")
            # print(f"   - Cần tìm key: '{emb_key}'")
            # print(f"   - Các key hiện có trong RAM: {list(self.embeddings.keys())}")
            
            # if emb_key not in self.embeddings:
            #     print(f"   ❌ LỖI: Không tìm thấy ma trận vector '{emb_key}'!")
            # else:
            #     print(f"   ✅ Đã tìm thấy ma trận vector. Shape: {self.embeddings[emb_key].shape}")
            
            # Tính toán
            if emb_key in self.embeddings and self.embeddings[emb_key] is not None:
                raw_bge = cosine_similarity(vec_bge, self.embeddings[emb_key]).flatten()
                if max(indices) < len(raw_bge):
                    sub_bge = raw_bge[indices]
                else:
                    sub_bge = np.zeros(len(indices))
            else:
                sub_bge = np.zeros(len(indices))

            print(len(indices), max(indices), len(vec_bge), len(raw_bge))
            
        except Exception as e:
            print(f"⚠️ Ensemble BGE Error: {e}")
            sub_bge = np.zeros(len(indices))

        # --- C. Tổng hợp (Weighted Sum) ---
        # Chuẩn hóa về [0, 1] trước khi cộng
        norm_tfidf = self.normalize_scores(sub_tfidf)
        norm_bge = self.normalize_scores(sub_bge)

        # Công thức Ensemble: 0.7 * Semantic + 0.3 * Keyword
        final_scores = 0.7 * norm_bge + 0.3 * norm_tfidf

        # Map kết quả
        df_results = df_jobs.copy()
        df_results['similarity_score'] = final_scores
        return df_results.nlargest(top_k, 'similarity_score')

    # =========================================================
    # 2. RECOMMENDATION FUNCTIONS (Dùng Ensemble)
    # =========================================================
    
    def get_recommendation_ensemble(self, job_content, df_full, top_k=10, exclude_id=None):
        """
        Dùng cho: Gợi ý công việc tương tự (Item-to-Item)
        Sử dụng Ensemble Search với 'overall' content.
        """
        df_results = self.search_ensemble(
            query=job_content, 
            df_jobs=df_full, 
            search_field="overall", # Luôn dùng overall cho gợi ý để chính xác nhất
            top_k=top_k + 1
        )
        
        if exclude_id is not None:
            df_results = df_results[df_results.index != exclude_id]
            
        return df_results.head(top_k)

    def get_user_recommendation(self, viewed_ids, df_full, top_k=20):
        """
        Dùng cho: Gợi ý trang chủ (User Personalization)
        Dựa trên lịch sử xem -> Tạo Query -> Ensemble Search
        """
        valid_ids = [i for i in viewed_ids if i in df_full.index]
        if not valid_ids: return pd.DataFrame()

        # Lấy 5 job gần nhất để tạo context (tránh nhiễu nếu lấy quá nhiều)
        recent_jobs = df_full.loc[valid_ids].tail(5)
        
        # Ghép Title lại thành 1 câu query dài
        combined_query = " ".join(recent_jobs['overall_text_processed'].astype(str).tolist())
        
        # Gọi Ensemble Search
        df_results = self.search_ensemble(
            query=combined_query, 
            df_jobs=df_full, 
            search_field="overall", 
            top_k=top_k + len(valid_ids)
        )
        
        # Lọc bỏ những job đã xem
        df_results = df_results[~df_results.index.isin(valid_ids)]
        return df_results.head(top_k)

    # =========================================================
    # 3. SINGLE MODEL FUNCTIONS (Cho Search riêng lẻ)
    # =========================================================
    
    # --- TF-IDF ---
    def load_tfidf(self, key):
        if key in self.models: return
        print(f"🔄 TF-IDF: Loading {key}...")
        self.models[key] = joblib.load(settings.MODEL_PATHS[key])
        self.embeddings[f"{key}_matrix"] = joblib.load(settings.EMBEDDING_PATHS[key])

    def search_tfidf(self, query, df_jobs, search_field, top_k):
        key = "tfidf_basic" if search_field == "title" else "tfidf_upgrade"
        self.load_tfidf(key)
        query_str = self.preprocess_text(query)
        vec = self.models[key].transform([query_str])
        scores = cosine_similarity(vec, self.embeddings[f"{key}_matrix"]).flatten()
        return self._safe_map_results(df_jobs, scores, top_k)

    # --- WORD2VEC ---
    def load_w2v(self, key):
        if key in self.models: return
        if key not in settings.MODEL_PATHS: return
        print(f"🔄 Word2Vec: Loading {key}...")
        try:
            self.models[key] = KeyedVectors.load(settings.MODEL_PATHS[key])
            emb_conf = settings.EMBEDDING_PATHS.get(key, {})
            if emb_conf:
                if emb_conf.get("title"): self.embeddings[f"{key}_title"] = np.load(emb_conf["title"])
                if emb_conf.get("overall"): self.embeddings[f"{key}_overall"] = np.load(emb_conf["overall"])
            print(f"✅ Loaded {key}")
        except Exception as e:
            print(f"❌ Load W2V Error: {e}")

    def _get_avg_vector(self, text, model):
        words = self.preprocess_tokens(text)
        valid = [w for w in words if w in model]

        # if len(text) < 100: 
        #     print(f"🔎 Query: '{text}'")
        #     print(f"   Tokens gốc: {words}")
        #     print(f"   Valid W2V:  {valid}") # <--- QUAN TRỌNG: Xem danh sách này có rỗng hoặc toàn từ rác không?

        if not valid: return np.zeros(model.vector_size)
        return np.mean([model[w] for w in valid], axis=0)

    def search_w2v(self, query, df_jobs, model_name, search_field, top_k):
        is_sg = "_sg" in model_name
        base = "w2v_average"
        suffix = "basic" if search_field == "title" else "upgrade"
        target_key = f"{base}_{suffix}" + ("_sg" if is_sg else "")

        self.load_w2v(target_key)
        if target_key not in self.models: return pd.DataFrame()

        query_vec = self._get_avg_vector(query, self.models[target_key])
        emb_key = f"{target_key}_{search_field}"
        if emb_key not in self.embeddings: # Fallback
            emb_key = f"{target_key}_title" if search_field == "overall" else f"{target_key}_overall"
            if emb_key not in self.embeddings: return pd.DataFrame()

        scores = cosine_similarity(query_vec.reshape(1, -1), self.embeddings[emb_key]).flatten()
        return self._safe_map_results(df_jobs, scores, top_k)

    # --- DOC2VEC ---
    def load_doc2vec(self, key):
        if key in self.models: return
        if key not in settings.MODEL_PATHS: return
        print(f"🔄 Doc2Vec: Loading {key}...")
        try:
            self.models[key] = Doc2Vec.load(settings.MODEL_PATHS[key])
            emb_conf = settings.EMBEDDING_PATHS.get(key, {})
            if emb_conf:
                if emb_conf.get("title"): self.embeddings[f"{key}_title"] = np.load(emb_conf["title"])
                if emb_conf.get("overall"): self.embeddings[f"{key}_overall"] = np.load(emb_conf["overall"])
            print(f"✅ Loaded {key}")
        except Exception as e:
            print(f"❌ Load Doc2Vec Error: {e}")

    def search_doc2vec(self, query, df_jobs, model_name, search_field, top_k):
        is_dbow = "dbow" in model_name
        base = "w2v_doc2vec"
        suffix = "basic" if search_field == "title" else "upgrade"
        target_key = f"{base}_{suffix}" + ("_dbow" if is_dbow else "")

        self.load_doc2vec(target_key)
        if target_key not in self.models: return pd.DataFrame()

        tokens = self.preprocess_tokens(query)
        query_vec = self.models[target_key].infer_vector(tokens, epochs=20)
        
        emb_key = f"{target_key}_{search_field}"
        if emb_key not in self.embeddings: # Fallback
            emb_key = f"{target_key}_title" if search_field == "overall" else f"{target_key}_overall"
            if emb_key not in self.embeddings: return pd.DataFrame()

        scores = cosine_similarity(query_vec.reshape(1, -1), self.embeddings[emb_key]).flatten()
        return self._safe_map_results(df_jobs, scores, top_k)

    # --- TRANSFORMER ---
    def load_transformer(self, key):
        if key in self.models: return
        print(f"🔄 Transformer: Loading {key}...")
        try:
            self.models[key] = SentenceTransformer(
                settings.MODEL_PATHS[key], 
                model_kwargs={"low_cpu_mem_usage": False},
                device="cpu" 
            )
            self.models[key].eval()  
            emb = settings.EMBEDDING_PATHS.get(key)
            if emb:
                if emb.get("title"): self.embeddings[f"{key}_title"] = np.load(emb["title"])
                if emb.get("overall"): self.embeddings[f"{key}_overall"] = np.load(emb["overall"])
            print(f"✅ Loaded {key}")
        except Exception as e:
            print(f"❌ Load Transformer Error: {e}")

    def search_transformer(self, query, df_jobs, model_name, search_field, top_k):
        suffix = "basic" if search_field == "title" else "upgrade"
        family = "mpnet"
        if "bge" in model_name: family = "bge_m3"
        elif "labse" in model_name: family = "labse"
        target_key = f"{family}_{suffix}"

        self.load_transformer(target_key)
        if target_key not in self.models: return pd.DataFrame()

        query_str = self.preprocess_text(query)
        vec = self.models[target_key].encode([query_str], normalize_embeddings=True)
        
        emb_key = f"{target_key}_{search_field}"
        if emb_key not in self.embeddings: # Fallback
            emb_key = f"{target_key}_title" if search_field == "overall" else f"{target_key}_overall"
            if emb_key not in self.embeddings: return pd.DataFrame()

        scores = cosine_similarity(vec, self.embeddings[emb_key]).flatten()
        return self._safe_map_results(df_jobs, scores, top_k)

    # =========================================================
    # MAIN DISPATCHER
    # =========================================================
    def search(self, query, df_jobs, model_name="ensemble", search_field="title", top_k=20):
        """
        Dispatcher trung tâm:
        - Nếu model_name='ensemble' -> Gọi hàm Ensemble.
        - Nếu khác -> Gọi các hàm Single Model.
        """
        # 1. Ensemble (Mô hình chính)
        if model_name == "ensemble":
            return self.search_ensemble(query, df_jobs, search_field, top_k)

        # 2. TF-IDF
        elif "tfidf" in model_name:
            return self.search_tfidf(query, df_jobs, search_field, top_k)

        # 3. Doc2Vec
        elif "doc2vec" in model_name:
            return self.search_doc2vec(query, df_jobs, model_name, search_field, top_k)

        # 4. Word2Vec
        elif "w2v" in model_name:
            return self.search_w2v(query, df_jobs, model_name, search_field, top_k)

        # 5. Transformers (MPNet, BGE, LaBSE)
        elif any(x in model_name for x in ["mpnet", "bge", "labse"]):
            return self.search_transformer(query, df_jobs, model_name, search_field, top_k)

        else:
            print(f"⚠️ Model không hỗ trợ: {model_name}")
            return pd.DataFrame()
        
    def warmup(self):

        print("Đang khởi động hệ thống")

        
        self.load_tfidf("tfidf_basic")
        self.load_tfidf("tfidf_upgrade")
        self.load_transformer("bge_m3_basic") 
        self.load_transformer("bge_m3_upgrade")
        
        self.load_transformer("mpnet_basic")
        self.load_transformer("mpnet_upgrade")
        self.load_transformer("labse_basic")
        self.load_transformer("labse_upgrade")
        self.load_w2v("w2v_average_basic")
        self.load_w2v("w2v_average_upgrade")
        self.load_w2v("w2v_average_basic_sg")
        self.load_w2v("w2v_average_upgrade_sg")

        self.load_doc2vec("w2v_doc2vec_basic")
        self.load_doc2vec("w2v_doc2vec_upgrade")
        self.load_doc2vec("w2v_doc2vec_basic_dbow")
        self.load_doc2vec("w2v_doc2vec_upgrade_dbow")
        
        print("Hệ thống đã sẵn sàng! (Warmup complete)")
search_engine = SearchEngine()
search_engine.warmup()