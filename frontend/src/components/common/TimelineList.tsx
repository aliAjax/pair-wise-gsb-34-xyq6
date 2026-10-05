import type { ReactNode } from "react";

export interface TimelineEntry {
  key: string;
  title: string;
  time?: string | null;
  description?: string;
  badge?: ReactNode;
}

export function TimelineList({ entries, emptyTitle = "暂无流转记录" }: {
  entries: TimelineEntry[];
  emptyTitle?: string;
}) {
  if (entries.length === 0) {
    return <p className="muted">{emptyTitle}</p>;
  }
  return (
    <ol className="timeline">
      {entries.map((entry) => (
        <li key={entry.key} className="timeline-item">
          <span className="timeline-dot" />
          <div className="timeline-body">
            <div className="timeline-head">
              <strong>{entry.title}</strong>
              {entry.badge}
            </div>
            {entry.description ? <p>{entry.description}</p> : null}
            {entry.time ? <time>{entry.time}</time> : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
