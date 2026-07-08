import React from 'react';

export default function SkeletonJobCard() {
  return (
    <div className="skeleton-card">
      <div>
        <div className="skeleton skeleton-title"></div>
        <div className="skeleton skeleton-text"></div>
      </div>
      <div className="skeleton-tags">
        <div className="skeleton skeleton-tag"></div>
        <div className="skeleton skeleton-tag"></div>
        <div className="skeleton skeleton-tag"></div>
      </div>
    </div>
  );
}