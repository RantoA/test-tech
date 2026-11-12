import type { ReactNode } from "react";

export function AuthCard({
  title,
  description,
  children,
  footer,
}: {
  title: string;
  description: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="mx-auto w-full max-w-md px-4 py-16">
      <div className="border border-line bg-surface p-8">
        <h1 className="text-xl font-semibold tracking-tight text-ink">{title}</h1>
        <p className="mt-1 text-sm text-muted">{description}</p>
        <div className="mt-8">{children}</div>
      </div>
      <p className="mt-6 text-center text-sm text-muted">{footer}</p>
    </div>
  );
}
