"use client";

import type { ReactNode } from "react";
import { Toaster } from "sonner";

import { AuthProvider } from "@/contexts/AuthContext";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <Toaster
        position="top-right"
        closeButton
        toastOptions={{
          classNames: {
            toast: "!rounded-none !border !border-line !shadow-none !font-sans",
          },
        }}
      />
    </AuthProvider>
  );
}
