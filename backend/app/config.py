import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings:
    # 1. DATA
    DATA_PATH = os.path.join(BASE_DIR, "data", "df_processed.xlsx")
    STOPWORDS_PATH = os.path.join(BASE_DIR, "vietnamese-stopwords-dash.txt")
    SIMILARITY_MATRIX_PATH = os.path.join(BASE_DIR, "job_cosine_similarities.pkl")

    # 2. MODEL PATHS
    MODEL_PATHS = {
       
        # MPNet
        "mpnet_basic": os.path.join(BASE_DIR, "paraphrase_multilingual_mpnet_model_vn_basic"),
        "mpnet_upgrade": os.path.join(BASE_DIR, "paraphrase_multilingual_mpnet_model_vn_upgrade"),
        
        # BGE-M3
        "bge_m3_basic": os.path.join(BASE_DIR, "bge_m3_model_vn_basic"),
        "bge_m3_upgrade": os.path.join(BASE_DIR, "bge_m3_model_vn_upgrade"),

        # LaBSE
        "labse_basic": os.path.join(BASE_DIR, "labse_model_vn_basic"),
        "labse_upgrade": os.path.join(BASE_DIR, "labse_model_vn_upgrade"),

        # TF-IDF
        "tfidf_basic": os.path.join(BASE_DIR, "tfidf_model_vi_basic.joblib"),
        "tfidf_upgrade": os.path.join(BASE_DIR, "tfidf_model_vi_upgrade.joblib"),

        # Word2Vec Average
        "w2v_average_basic": os.path.join(BASE_DIR, "word2vec_average_basic.kv"),
        "w2v_average_upgrade": os.path.join(BASE_DIR, "word2vec_average_upgrade.kv"),
        "w2v_average_basic_sg": os.path.join(BASE_DIR, "word2vec_average_basic_sg.kv"),
        "w2v_average_upgrade_sg": os.path.join(BASE_DIR, "word2vec_average_upgrade_sg.kv"),

        # Doc2Vec (Đã bổ sung Upgrade)
        "w2v_doc2vec_basic": os.path.join(BASE_DIR, "word2vec_doc2vec_basic.model"),
        "w2v_doc2vec_upgrade": os.path.join(BASE_DIR, "word2vec_doc2vec_upgrade.model"),
        
        "w2v_doc2vec_basic_dbow": os.path.join(BASE_DIR, "word2vec_doc2vec_basic_dbow.model"),
        "w2v_doc2vec_upgrade_dbow": os.path.join(BASE_DIR, "word2vec_doc2vec_upgrade_dbow.model"),
    }

    # 3. EMBEDDING PATHS
    EMBEDDING_PATHS = {
        
        # MPNET
        "mpnet_basic": { 
            "title": os.path.join(BASE_DIR, "job_title_embeddings_mpnet_vn_basic.npy"), 
            "overall": None 
        },
        "mpnet_upgrade": { 
            "title": None, 
            "overall": os.path.join(BASE_DIR, "job_text_embeddings_mpnet_vn_upgrade.npy") 
        },

        # BGE-M3
        "bge_m3_basic": {
             "title": os.path.join(BASE_DIR, "job_title_embeddings_bge_m3_vn_basic.npy"), 
             "overall": None
        }, 
        "bge_m3_upgrade": {
             "title": None,
             "overall": os.path.join(BASE_DIR, "job_text_embeddings_bge_m3_vn_upgrade.npy")
        },

        # LaBSE
        "labse_basic": {
             "title": os.path.join(BASE_DIR, "job_title_embeddings_labse_vn_basic.npy"),
             "overall": None
        },
        "labse_upgrade": {
             "title": None,
             "overall": os.path.join(BASE_DIR, "job_text_embeddings_labse_vn_upgrade.npy")
        },

        # TF-IDF
        "tfidf_basic": os.path.join(BASE_DIR, "tfidf_matrix_basic.pkl"),
        "tfidf_upgrade": os.path.join(BASE_DIR, "tfidf_matrix_upgrade.pkl"),

        # Word2Vec Average
        "w2v_average_basic": { "title": os.path.join(BASE_DIR, "job_title_embeddings_w2v_ave_vn_basic.npy"), "overall": None },
        "w2v_average_upgrade": { "title": None, "overall": os.path.join(BASE_DIR, "job_text_embeddings_w2v_ave_vn_upgrade.npy") },
        "w2v_average_basic_sg": { "title": os.path.join(BASE_DIR, "job_title_embeddings_w2v_ave_vn_basic_sg.npy"), "overall": None },
        "w2v_average_upgrade_sg": { "title": None, "overall": os.path.join(BASE_DIR, "job_text_embeddings_w2v_ave_vn_upgrade_sg.npy") },

        # Doc2Vec (PV-DM)
        "w2v_doc2vec_basic": { 
            "title": os.path.join(BASE_DIR, "job_title_embeddings_doc2vec_vn_basic.npy"), 
            "overall": None 
        },
        "w2v_doc2vec_upgrade": { 
            "title": None, 
            "overall": os.path.join(BASE_DIR, "job_text_embeddings_doc2vec_vn_upgrade.npy") 
        },

        # Doc2Vec (PV-DBOW)
        "w2v_doc2vec_basic_dbow": { 
            "title": os.path.join(BASE_DIR, "job_title_embeddings_doc2vec_vn_basic_dbow.npy"),
            "overall": None 
        },
        "w2v_doc2vec_upgrade_dbow": { 
            "title": None, 
            "overall": os.path.join(BASE_DIR, "job_text_embeddings_doc2vec_vn_upgrade_dbow.npy") 
        },
    }

settings = Settings()

