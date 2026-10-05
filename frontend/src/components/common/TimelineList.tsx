import type { AuditLog } from "../../types/AuditLog";
import { formatDateTime } from "../../utils/formatters";
import { EmptyState } from "./EmptyState";

type TimelineItem = {
  id: number | string;
  title: string;
  detail?: string | null;
  time?: string | null;
  tone?: string;
};

// 通用时间线：隐患页传流转记录、审计页传操作日志。
export function TimelineList({ items }: { items: TimelineItem[] }) {
  if (!items.length) return <EmptyState title="暂无流转记录" />;
  return (
    <ol className="timeline">
      {items.map((item) => (
        <li key={item.id} className={`timeline-item ${item.tone ? `tone-${item.tone}` : ""}`}>
          <div className="timeline-dot" />
          <div className="timeline-body">
            <div className="timeline-title">{item.title}</div>
            {item.detail && <div className="timeline-detail">{item.detail}</div>}
            {item.time && <time className="timeline-time">{formatDateTime(item.time)}</time>}
          </div>
        </li>
      ))}
    </ol>
  );
}

export function auditLogToTimeline(log: AuditLog): TimelineItem {
  return {
    id: log.id,
    title: `${log.actor} · ${log.action}`,
    detail: log.detail,
    time: log.created_at,
  };
}
