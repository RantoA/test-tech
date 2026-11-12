"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Button, ButtonLink } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/utils/cn";

import { Container } from "./Container";

const privateLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/posts/new", label: "New post" },
  { href: "/profile", label: "Profile" },
];

export function Header() {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
    } finally {
      setLoggingOut(false);
      setMenuOpen(false);
    }
  };

  const navLink = (href: string, label: string) => (
    <Link
      key={href}
      href={href}
      onClick={() => setMenuOpen(false)}
      className={cn(
        "text-sm transition-colors",
        pathname === href ? "font-medium text-ink" : "text-muted hover:text-ink",
      )}
    >
      {label}
    </Link>
  );

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface">
      <Container className="flex h-16 items-center justify-between gap-6">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-base font-semibold tracking-tight text-ink">
            my-blog
          </Link>
          <nav className="hidden items-center gap-6 md:flex">
            {navLink("/", "Articles")}
            {user && privateLinks.map((link) => navLink(link.href, link.label))}
          </nav>
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {loading ? null : user ? (
            <>
              <span className="text-sm text-muted">{user.name}</span>
              <Button variant="secondary" size="sm" onClick={handleLogout} loading={loggingOut}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <ButtonLink href="/login" variant="ghost" size="sm">
                Log in
              </ButtonLink>
              <ButtonLink href="/register" size="sm">
                Sign up
              </ButtonLink>
            </>
          )}
        </div>

        <button
          type="button"
          className="inline-flex h-9 w-9 items-center justify-center border border-line-strong md:hidden"
          aria-label="Toggle navigation"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {menuOpen ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </Container>

      {menuOpen && (
        <div className="border-t border-line bg-surface md:hidden">
          <Container className="flex flex-col gap-4 py-4">
            {navLink("/", "Articles")}
            {user && privateLinks.map((link) => navLink(link.href, link.label))}
            <div className="flex gap-2 border-t border-line pt-4">
              {user ? (
                <Button variant="secondary" size="sm" onClick={handleLogout} loading={loggingOut}>
                  Log out
                </Button>
              ) : (
                <>
                  <ButtonLink href="/login" variant="secondary" size="sm" onClick={() => setMenuOpen(false)}>
                    Log in
                  </ButtonLink>
                  <ButtonLink href="/register" size="sm" onClick={() => setMenuOpen(false)}>
                    Sign up
                  </ButtonLink>
                </>
              )}
            </div>
          </Container>
        </div>
      )}
    </header>
  );
}
