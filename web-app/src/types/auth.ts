/**
 * TypeScript type definitions for authentication.
 *
 * Mirrors the backend schemas in api-server/app/schemas/auth.py
 * and the UserRole enum in api-server/app/models/user.py.
 */

export enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  ADMIN = "admin",
  SUPER_ADMIN = "super_admin",
}

/** Represents a user account as returned by the API. */
export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  /** ISO 8601 datetime string, e.g. "2024-01-15T10:30:00Z" */
  created_at: string;
}

/**
 * Decoded JWT payload.
 *
 * - sub  : user id (UUID string)
 * - role : UserRole of the authenticated user
 * - jti  : JWT ID — used for token blacklisting on logout
 * - exp  : expiry timestamp (Unix epoch seconds)
 */
export interface TokenPayload {
  sub: string;
  role: UserRole;
  jti: string;
  exp: number;
}

/** Credentials submitted to POST /api/v1/auth/login */
export interface LoginRequest {
  email: string;
  password: string;
}

/** JWT access token returned after a successful login */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}
