import React from 'react';

export default function SearchBar({ 
  query, setQuery, 
  modelName, setModelName, 
  searchType, setSearchType, // [MỚI] Nhận thêm props này
  onSearch 
}) {
  return (
    <div className="modern-search-bar">
      {/* 1. Dropdown Model */}
      <div style={{ position: 'relative' }}>
        <select
          className="search-select-modern"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
        >
          <option value="ensemble">✨ Ensemble</option>
          <option value="bge">🌌 BGE-M3</option>
          <option value="mpnet">🤖 MPNet</option>
          <option value="doc2vec">📄 Doc2Vec</option>
          <option value="tfidf">📊 TF-IDF</option>
          <option value="w2v">🧠 Word2Vec</option>
        </select>
      </div>

      <div className="search-divider"></div>

      {/* 2. [QUAN TRỌNG] Dropdown Phạm vi (Title/Overall) */}
      {/* Chỉ hiện nếu Dashboard truyền props này xuống */}
      {searchType && setSearchType && (
        <>
          <select 
            className="search-select-modern" 
            style={{minWidth: '110px', color: '#334155'}}
            value={searchType} 
            onChange={(e) => setSearchType(e.target.value)}
          >
            <option value="overall">📝 Tất cả</option>
            <option value="title">🏷️ Tiêu đề</option>
          </select>
          <div className="search-divider"></div>
        </>
      )}

      {/* 3. Input */}
      <input
        type="text"
        className="search-input-modern"
        placeholder="Nhập kỹ năng, chức vụ (vd: Java, Marketing)..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch()}
      />

      {/* 4. Button */}
      <button onClick={onSearch} className="search-btn-modern">
        Tìm kiếm
      </button>
    </div>
  );
}