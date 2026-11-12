import { NextResponse, type NextRequest } from "next/server";

import { isGuestOnlyPath, isPrivatePath } from "@/utils/routes";

const SESSION_COOKIE = "access_token";

/**
 * Optimistic route protection based on the presence of the HttpOnly session cookie.
 * This only improves UX: the API remains the authority and rejects invalid tokens (401).
 */
export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);

  if (isPrivatePath(pathname) && !hasSession) {
    const url = new URL("/login", request.url);
    url.searchParams.set("next", `${pathname}${search}`);
    return NextResponse.redirect(url);
  }

  if (isGuestOnlyPath(pathname) && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/profile/:path*", "/posts/:path*", "/login", "/register"],
};
