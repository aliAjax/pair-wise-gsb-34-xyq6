import type { ReactNode } from "react";

export function PageHeader({ title, eyebrow = "fire-inspect", actions }: {
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
}) {
  return (
    <section className="page-head">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </section>
  );
}
