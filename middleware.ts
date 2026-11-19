import { auth } from "@/lib/auth/config";
import { NextResponse } from "next/server";

function isAdminPath(pathname: string): boolean {
  return pathname.startsWith("/admin");
}

function isDashboardPath(pathname: string): boolean {
  return pathname.startsWith("/dashboard");
}

export default auth((req) => {
  const { pathname } = req.nextUrl;

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

  // Everything else — a public page, a static asset, or a path with no route — falls through, and the
  // router answers 404 rather than redirecting a dead URL to sign-in and telling a crawler it moved.
  // Do not add an early `return` above the guards: `/admin` and `/dashboard` are the only surfaces this
  // file protects, and a path ending in `.ext` is still a path they must see.
  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
