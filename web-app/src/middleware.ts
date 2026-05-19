/**
 * Next.js Edge Runtime middleware — server-side route protection.
 *
 * Runs before every request that matches the `config.matcher` pattern.
 * Uses `jose.decodeJwt` (no signature verification) to read the JWT payload
 * from the `access_token` cookie and enforces role-based access control.
 *
 * Logic:
 *  1. Public path  → NextResponse.next()
 *  2. Protected path + no token → redirect /login
 *  3. Protected path + expired token → redirect /login
 *  4. Protected path + insufficient role → redirect /403
 *  5. Otherwise → NextResponse.next()
 *
 * Requirements: 2
 */

import { NextRequest, NextResponse } from "next/server";
import { decodeJwt } from "jose";

// ---------------------------------------------------------------------------
// Types (inlined to avoid importing from @/types which may not be Edge-safe)
// ---------------------------------------------------------------------------

enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  ADMIN = "admin",
  SUPER_ADMIN = "super_admin",
}

interface TokenPayload {
  sub: string;
  role: UserRole;
  jti: string;
  exp: number;
}

// ---------------------------------------------------------------------------
// Route classification
// ---------------------------------------------------------------------------

/** Paths that are always accessible without authentication. */
const PUBLIC_PATHS: string[] = [
  "/login",
  "/forgot-password",
  "/reset-password",
  "/403",
  "/",
];

/** Prefixes that require authentication (and possibly a specific role). */
const PROTECTED_PREFIXES: string[] = [
  "/student/",
  "/teacher/",
  "/admin/",
  "/dashboard/",
];

/** Returns true if the pathname is a public route. */
function isPublicPath(pathname: string): boolean {
  // Exact public paths
  if (PUBLIC_PATHS.includes(pathname)) return true;

  // Next.js API auth routes are always public
  if (pathname.startsWith("/api/auth/")) return true;

  return false;
}

/** Returns true if the pathname requires authentication. */
function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

// ---------------------------------------------------------------------------
// Role hierarchy
// ---------------------------------------------------------------------------

const ROLE_HIERARCHY: UserRole[] = [
  UserRole.STUDENT,
  UserRole.TEACHER,
  UserRole.ADMIN,
  UserRole.SUPER_ADMIN,
];

function roleRank(role: UserRole): number {
  return ROLE_HIERARCHY.indexOf(role);
}

// ---------------------------------------------------------------------------
// Role requirements per route prefix
// ---------------------------------------------------------------------------

const ROUTE_ROLE_REQUIREMENTS: Array<{ prefix: string; minRole: UserRole }> = [
  { prefix: "/admin/", minRole: UserRole.ADMIN },
  { prefix: "/teacher/", minRole: UserRole.TEACHER },
  { prefix: "/student/", minRole: UserRole.STUDENT },
  { prefix: "/dashboard/", minRole: UserRole.STUDENT },
];

/**
 * Returns true if `userRole` meets the minimum role required for `pathname`.
 * Paths with no matching rule are considered accessible to any authenticated user.
 */
function hasRequiredRole(userRole: UserRole, pathname: string): boolean {
  for (const { prefix, minRole } of ROUTE_ROLE_REQUIREMENTS) {
    if (pathname.startsWith(prefix)) {
      return roleRank(userRole) >= roleRank(minRole);
    }
  }
  return true;
}

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------

/**
 * Decode the JWT string and return a `TokenPayload`, or `null` if the token
 * is malformed or missing required fields.
 */
function decodeToken(token: string): TokenPayload | null {
  try {
    const raw = decodeJwt(token);

    if (
      typeof raw.sub !== "string" ||
      typeof raw.jti !== "string" ||
      typeof raw.exp !== "number" ||
      typeof raw.role !== "string"
    ) {
      return null;
    }

    if (!Object.values(UserRole).includes(raw.role as UserRole)) {
      return null;
    }

    return {
      sub: raw.sub,
      role: raw.role as UserRole,
      jti: raw.jti,
      exp: raw.exp,
    };
  } catch {
    return null;
  }
}

/** Returns true if the token payload's expiry time is in the past. */
function isTokenExpired(payload: TokenPayload): boolean {
  return payload.exp * 1000 < Date.now();
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  // 1. Public path — always allow
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // 2. Not a protected path — allow (e.g. static assets caught by matcher)
  if (!isProtectedPath(pathname)) {
    return NextResponse.next();
  }

  // 3. Protected path — check token
  const tokenValue = request.cookies.get("access_token")?.value;

  if (!tokenValue) {
    // No token → redirect to login
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const payload = decodeToken(tokenValue);

  if (!payload) {
    // Malformed token → redirect to login
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isTokenExpired(payload)) {
    // Expired token → redirect to login
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (!hasRequiredRole(payload.role, pathname)) {
    // Insufficient role → redirect to 403
    return NextResponse.redirect(new URL("/403", request.url));
  }

  // All checks passed
  return NextResponse.next();
}

// ---------------------------------------------------------------------------
// Matcher — only run middleware on relevant paths
// ---------------------------------------------------------------------------

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     * - _next/static  (static files)
     * - _next/image   (image optimisation)
     * - favicon.ico
     * - Any file with an extension (e.g. .png, .svg, .js, .css)
     */
    "/((?!_next/static|_next/image|favicon\\.ico|.*\\..*).*)",
  ],
};
