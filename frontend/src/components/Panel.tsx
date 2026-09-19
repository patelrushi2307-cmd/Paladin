import type { ReactNode } from 'react';

export function Panel({ 
  title, 
  eyebrow, 
  children, 
  className = '',
  badge
}: { 
  title: string; 
  eyebrow?: string; 
  children: ReactNode; 
  className?: string;
  badge?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-heading">
        <div className="panel-title-area">
          <span className="eyebrow">{eyebrow ?? 'PALADIN PASSIVE SENSOR'}</span>
          <h2>{title}</h2>
        </div>
        {badge ? (
          <span className="panel-badge">{badge}</span>
        ) : (
          <span className="panel-badge">ENCLAVE SECURE</span>
        )}
      </div>
      {children}
    </section>
  );
}
