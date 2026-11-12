"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { Container } from "@/components/layout/Container";
import { PageLoader } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";

/** Client-side guard for private pages (complements the proxy and the API checks). */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [loading, user, router, pathname]);

  if (loading || !user) return <PageLoader label="Checking your session…" />;
  return <Container className="py-10">{children}</Container>;
}
