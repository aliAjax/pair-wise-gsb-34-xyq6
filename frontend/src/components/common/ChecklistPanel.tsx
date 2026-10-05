import type { ReactNode } from "react";
import { useChecklistProgress } from "../../hooks/useChecklistProgress";
import type { ChecklistItem } from "../../types/InspectionTask";

interface ChecklistPanelProps {
  items: ChecklistItem[];
  version: number;
  renderItem?: (item: ChecklistItem, index: number) => ReactNode;
  footer?: ReactNode;
}

export function ChecklistPanel({ items, version, renderItem, footer }: ChecklistPanelProps) {
  const progress = useChecklistProgress(items);
  return (
    <div className="panel checklist-panel">
      <header className="panel-head">
        <h2>巡检检查项（清单 v{version}）</h2>
        <div className="progress-meta">
          已完成 {progress.submitted}/{progress.total}
          <span className="progress-bar">
            <i style={{ width: `${progress.percent}%` }} />
          </span>
          {progress.abnormal > 0 ? <span className="text-danger">异常 {progress.abnormal}</span> : null}
        </div>
      </header>
      <div className="checklist-rows">
        {items.length === 0 ? <p className="muted">暂无检查项</p> : null}
        {items.map((item, index) => (
          <div className="checklist-row" key={item.id}>
            {renderItem ? renderItem(item, index) : <DefaultRow item={item} />}
          </div>
        ))}
      </div>
      {footer}
    </div>
  );
}

function DefaultRow({ item }: { item: ChecklistItem }) {
  return (
    <div>
      <strong>{item.item_name}</strong>
      <span className="muted">
        {item.item_code} · v{item.checklist_version}
      </span>
    </div>
  );
}
