/**
 * TypeScript type definitions for problems.
 *
 * Mirrors the backend schemas in api-server/app/schemas/problem.py
 * and the Problem model in api-server/app/models/problem.py.
 */

/** Supported programming languages for a problem. */
export type Language = "python" | "cpp";

/** A problem as returned by the API. */
export interface Problem {
  id: string;
  code: string;
  title: string;
  statement_md: string | null;
  time_limit_ms: number;
  memory_limit_mb: number;
  allowed_languages: Language[];
  scoring_mode: string;
  is_visible: boolean;
  is_archived: boolean;
  package_path: string | null;
  created_by: string;
  /** ISO 8601 datetime string */
  created_at: string;
  /** ISO 8601 datetime string */
  updated_at: string;
}

/** Payload for creating a new problem. */
export interface ProblemCreate {
  code: string;
  title: string;
  time_limit_ms?: number;
  memory_limit_mb?: number;
  allowed_languages?: Language[];
  scoring_mode?: string;
  is_visible?: boolean;
}
