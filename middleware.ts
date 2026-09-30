import { auth } from "@/lib/auth/config";
import { NextResponse } from "next/server";

const publicPaths = [
  "/",
  "/about",
  "/api",
  "/calculator",
  "/docs",
  "/mcp",
  "/skills",
  "/pricing",
  "/terms",
  "/privacy",
  "/ai-advisor",
  "/sign-in",
  "/sign-up",
  "/v1/valuation",
  "/v1/mcp",
  "/v1/benchmarks",
  "/v1/ai",
  "/v1/billing/webhook",
  "/v1/auth",
  "/favicon.ico",
];

function isPublic(pathname: string): boolean {
  return publicPaths.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

function isAdminPath(pathname: string): boolean {
  return pathname.startsWith("/admin");
}

function isDashboardPath(pathname: string): boolean {
  return pathname.startsWith("/dashboard");
}

export default auth((req) => {
  const { pathname } = req.nextUrl;

  if (isPublic(pathname) || pathname.startsWith("/_next") || pathname.includes(".")) {
    return NextResponse.next();
  }

  const session = req.auth;
  const role = (session?.user as { role?: string } | undefined)?.role ?? "public";

  if (isAdminPath(pathname)) {
    if (!session) {
      return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, req.url));
    }
    if (role !== "admin") {
      return NextResponse.redirect(new URL("/", req.url));
    }
    return NextResponse.next();
  }

  if (isDashboardPath(pathname)) {
    if (!session) {
      return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, req.url));
    }
    return NextResponse.next();
  }

  if (!session) {
    return NextResponse.redirect(new URL(`/sign-in?callbackUrl=${encodeURIComponent(pathname)}`, req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
