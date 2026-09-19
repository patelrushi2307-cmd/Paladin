import type { ReactNode } from 'react';

export function MetricCard({ 
  label, 
  value, 
  detail, 
  tone = 'default',
  icon 
}: { 
  label: string; 
  value: string; 
  detail: string; 
  tone?: 'default' | 'amber' | 'cyan' | 'emerald' | 'rose';
  icon?: ReactNode;
}) {
  return (
    <div className={`metric-card-pro tone-${tone}`}>
      <div className="metric-card-header">
        <span>{label}</span>
        {icon && <div className="metric-icon-box">{icon}</div>}
      </div>
      <div className="metric-card-value">{value}</div>
      <div className="metric-card-detail">
        <span>{detail}</span>
      </div>
    </div>
  );
}
