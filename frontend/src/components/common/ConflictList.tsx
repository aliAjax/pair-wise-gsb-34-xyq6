import type { ResultConflict } from "../../types/InspectionResult";

export function ConflictList({ conflicts }: { conflicts: ResultConflict[] }) {
  if (conflicts.length === 0) return null;
  return (
    <div className="conflict-box">
      <h3>部分检查项未保存（{conflicts.length}）</h3>
      <ul>
        {conflicts.map((conflict) => (
          <li key={`${conflict.item_code}-${conflict.code}`}>
            <code>{conflict.item_code}</code>
            <span>{conflict.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
