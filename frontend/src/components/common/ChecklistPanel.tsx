import { useChecklistProgress } from "../../hooks/useChecklistProgress";
import type { ChecklistItem } from "../../types/InspectionTask";

type Props = {
  items: ChecklistItem[];
  resultMap: Record<string, string>;
  version: string;
  currentVersion: string;
};

// 巡检清单进度面板：展示完成率、异常数与清单版本冲突提示。
export function ChecklistPanel({ items, resultMap, version, currentVersion }: Props) {
  const progress = useChecklistProgress(items, resultMap);
  const stale = version !== currentVersion;
  return (
    <div className="panel checklist-panel">
      <div className="checklist-head">
        <h2>巡检清单</h2>
        <span className={`badge ${stale ? "tone-danger" : "tone-ok"}`}>
          清单版本 {currentVersion}
          {stale ? `（本地 ${version} 已过期）` : ""}
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress.percent}%` }} />
      </div>
      <p className="checklist-meta">
        已填 {progress.filled}/{progress.total} 项
        {progress.abnormal > 0 && <span className="danger-text">，其中异常 {progress.abnormal} 项</span>}
        {progress.remaining.length > 0 && <span className="muted">，待检：{progress.remaining.join("、")}</span>}
      </p>
    </div>
  );
}
