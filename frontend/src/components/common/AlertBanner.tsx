import type { ReactNode } from "react";

export function AlertBanner({ tone = "info", children, onClose }: {
  tone?: "info" | "success" | "warn" | "danger";
  children: ReactNode;
  onClose?: () => void;
}) {
  return (
    <div className={`alert alert-${tone}`} role="alert">
      <div className="alert-body">{children}</div>
      {onClose && <button className="alert-close" onClick={onClose} aria-label="关闭">×</button>}
    </div>
  );
}
