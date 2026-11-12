import type { ReactNode } from "react";

import { cn } from "@/utils/cn";

export function Alert({ tone = "error", children }: { tone?: "error" | "info"; children: ReactNode }) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={cn(
        "border-l-2 px-4 py-3 text-sm",
        tone === "error" ? "border-danger bg-danger-soft text-danger" : "border-accent bg-accent-soft text-accent",
      )}
    >
      {children}
    </div>
  );
}
