export function StatCard({ label, value, hint, tone = "default" }: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "default" | "danger" | "warn" | "ok";
}) {
  return (
    <div className={`stat stat-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {hint && <em>{hint}</em>}
    </div>
  );
}
