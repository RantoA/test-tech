"use client";

import { usePathname, useRouter } from "next/navigation";
import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { toast } from "sonner";

import { ApiError, UNAUTHORIZED_EVENT } from "@/services/api";
import { authService, type LoginInput, type RegisterInput } from "@/services/auth.service";
import { userService } from "@/services/user.service";
import type { User } from "@/types/user";
import { CSRF_COOKIE, getCookie } from "@/utils/cookies";
import { isPrivatePath } from "@/utils/routes";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (input: LoginInput) => Promise<User>;
  register: (input: RegisterInput) => Promise<User>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  setUser: (user: User) => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

/** Resolve the current user from the session cookie, clearing stale sessions. */
async function loadSession(): Promise<User | null> {
  // No session cookie at all: skip the network round-trip.
  if (!getCookie(CSRF_COOKIE)) return null;
  try {
    return await userService.me({ silentUnauthorized: true });
  } catch (error) {
    // Expired session: clear the cookies server-side (they are HttpOnly).
    if (error instanceof ApiError && error.status === 401) {
      await authService.logout().catch(() => undefined);
    }
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUserState] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setUserState(await loadSession());
  }, []);

  useEffect(() => {
    let active = true;
    void loadSession().then((sessionUser) => {
      if (!active) return;
      setUserState(sessionUser);
      setLoading(false);
    });
    return () => {
      active = false;
    };
  }, []);

  // Any 401 from the API means the session expired: reset and send the user to login.
  useEffect(() => {
    const onUnauthorized = () => {
      setUserState(null);
      void authService.logout().catch(() => undefined);
      if (isPrivatePath(window.location.pathname)) {
        toast.error("Your session has expired. Please log in again.");
        router.replace(`/login?next=${encodeURIComponent(window.location.pathname)}`);
      }
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, [router]);

  const login = useCallback(async (input: LoginInput) => {
    const payload = await authService.login(input);
    setUserState(payload.user);
    return payload.user;
  }, []);

  const register = useCallback(async (input: RegisterInput) => {
    const payload = await authService.register(input);
    setUserState(payload.user);
    return payload.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUserState(null);
      if (isPrivatePath(pathname)) router.replace("/login");
      router.refresh();
    }
  }, [pathname, router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
      refresh,
      setUser: setUserState,
    }),
    [user, loading, login, register, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
