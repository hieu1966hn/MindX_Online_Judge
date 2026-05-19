/**
 * Auth helper utilities for the web-app.
 *
 * - decodeToken   : decode a JWT string into a TokenPayload (no signature verification)
 * - isTokenExpired: check whether a decoded payload has passed its expiry time
 * - hasRequiredRole: check whether a user's role satisfies the route's minimum role
 * - getTokenFromCookie: read the raw access_token string from document.cookie
 */

import { decodeJwt } from "jose";
import { TokenPayload, UserRole } from "@/types";

// ---------------------------------------------------------------------------
// Role hierarchy — higher index = higher privilege
// ---------------------------------------------------------------------------
const ROLE_HIERARCHY: UserRole[] = [
  UserRole.STUDENT,
  UserRole.TEACHER,
  UserRole.ADMIN,
  UserRole.SUPER_ADMIN,
];

/**
 * Returns the numeric rank of a role (higher = more privileged).
 * Returns -1 for unknown roles so they always fail permission checks.
 */
function roleRank(role: UserRole): number {
  return ROLE_HIERARCHY.indexOf(role);
}

// ---------------------------------------------------------------------------
// Route → minimum required role mapping
// ---------------------------------------------------------------------------
const ROUTE_ROLE_REQUIREMENTS: Array<{ prefix: string; minRole: UserRole }> = [
  { prefix: "/admin/", minRole: UserRole.ADMIN },
  { prefix: "/teacher/", minRole: UserRole.TEACHER },
  { prefix: "/student/", minRole: UserRole.STUDENT },
];

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Decode a JWT string and return its payload as a `TokenPayload`.
 *
 * Uses `jose.decodeJwt` which performs **no signature verification** —
 * suitable for client-side display/routing decisions only.
 *
 * Returns `null` if the token is malformed or missing required fields.
 */
export function decodeToken(token: string): TokenPayload | null {
  try {
    const raw = decodeJwt(token);

    // Validate that the required fields are present and have the right types
    if (
      typeof raw.sub !== "string" ||
      typeof raw.jti !== "string" ||
      typeof raw.exp !== "number" ||
      typeof raw.role !== "string"
    ) {
      return null;
    }

    // Validate that the role value is a known UserRole
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

/**
 * Returns `true` if the token payload's expiry time is in the past.
 *
 * `payload.exp` is a Unix timestamp in **seconds**; `Date.now()` is in
 * milliseconds, so we multiply by 1000 before comparing.
 */
export function isTokenExpired(payload: TokenPayload): boolean {
  return payload.exp * 1000 < Date.now();
}

/**
 * Returns `true` if `userRole` meets the minimum role required for
 * `pathname`.
 *
 * Route rules:
 *   /student/* → requires at least STUDENT
 *   /teacher/* → requires at least TEACHER
 *   /admin/*   → requires at least ADMIN
 *
 * Paths that don't match any rule are considered public and always return
 * `true`.
 */
export function hasRequiredRole(userRole: UserRole, pathname: string): boolean {
  for (const { prefix, minRole } of ROUTE_ROLE_REQUIREMENTS) {
    if (pathname.startsWith(prefix)) {
      return roleRank(userRole) >= roleRank(minRole);
    }
  }
  // No matching rule → public route
  return true;
}

/**
 * Reads the `access_token` value from `document.cookie`.
 *
 * Returns `null` when:
 * - running in a non-browser environment (SSR / Edge Runtime)
 * - the cookie is not present
 */
export function getTokenFromCookie(): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const match = document.cookie
    .split("; ")
    .find((part) => part.startsWith("access_token="));

  if (!match) {
    return null;
  }

  const value = match.slice("access_token=".length);
  return value || null;
}
