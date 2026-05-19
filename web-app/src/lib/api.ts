/**
 * Browser-side API client for the MindX Online Judge backend.
 *
 * Base URL is read from the NEXT_PUBLIC_API_URL environment variable,
 * falling back to http://localhost:8000 for local development.
 *
 * All authenticated requests automatically attach an
 * `Authorization: Bearer <token>` header by reading the `access_token`
 * cookie from `document.cookie`.
 */

import type {
  LoginResponse,
  Problem,
  ProblemCreate,
  Submission,
  SubmissionCreate,
} from "@/types";

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/**
 * Read the `access_token` value from `document.cookie`.
 * Returns an empty string when running server-side or when the cookie is absent.
 */
function getAccessToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith("access_token="));
  return match ? match.split("=").slice(1).join("=") : "";
}

/** Build the common headers, optionally including the Authorization header. */
function buildHeaders(
  authenticated: boolean,
  extra?: Record<string, string>
): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extra,
  };
  if (authenticated) {
    const token = getAccessToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * Perform a fetch and throw a descriptive error when the response is not OK.
 * The error message is taken from the API response body when available.
 */
async function request<T>(
  path: string,
  options: RequestInit & { authenticated?: boolean } = {}
): Promise<T> {
  const { authenticated = true, ...fetchOptions } = options;

  // Merge in auth header unless the caller opted out
  if (authenticated) {
    const token = getAccessToken();
    if (token) {
      fetchOptions.headers = {
        ...(fetchOptions.headers as Record<string, string>),
        Authorization: `Bearer ${token}`,
      };
    }
  }

  const response = await fetch(`${BASE_URL}${path}`, fetchOptions);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      // FastAPI returns { detail: string | object }
      if (body?.detail) {
        message =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      // Body was not JSON — keep the default message
    }
    throw new Error(message);
  }

  // 204 No Content — return undefined cast to T
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

/**
 * Authenticate with email + password.
 * Returns a LoginResponse containing the JWT access token.
 *
 * POST /api/v1/auth/login
 */
export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  return request<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    authenticated: false,
  });
}

/**
 * Invalidate the given token on the server (adds its JTI to the blacklist).
 *
 * POST /api/v1/auth/logout
 */
export async function logout(token: string): Promise<void> {
  return request<void>("/api/v1/auth/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    authenticated: false,
  });
}

/**
 * Request a password-reset email for the given address.
 * Always returns the same response regardless of whether the email exists.
 *
 * POST /api/v1/auth/password-reset/request
 */
export async function requestPasswordReset(email: string): Promise<void> {
  return request<void>("/api/v1/auth/password-reset/request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
    authenticated: false,
  });
}

/**
 * Complete a password reset using the one-time token from the reset email.
 *
 * POST /api/v1/auth/password-reset/confirm
 */
export async function confirmPasswordReset(
  token: string,
  newPassword: string
): Promise<void> {
  return request<void>("/api/v1/auth/password-reset/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
    authenticated: false,
  });
}

// ---------------------------------------------------------------------------
// Problems
// ---------------------------------------------------------------------------

/**
 * Fetch the list of visible problems.
 *
 * GET /api/v1/problems/
 */
export async function getProblems(): Promise<Problem[]> {
  return request<Problem[]>("/api/v1/problems/", {
    method: "GET",
    headers: buildHeaders(true),
  });
}

/**
 * Fetch a single problem by its ID.
 *
 * GET /api/v1/problems/{id}
 */
export async function getProblem(id: string): Promise<Problem> {
  return request<Problem>(`/api/v1/problems/${id}`, {
    method: "GET",
    headers: buildHeaders(true),
  });
}

/**
 * Create a new problem (Teacher+ only).
 *
 * POST /api/v1/problems/
 */
export async function createProblem(data: ProblemCreate): Promise<Problem> {
  return request<Problem>("/api/v1/problems/", {
    method: "POST",
    headers: buildHeaders(true),
    body: JSON.stringify(data),
  });
}

/**
 * Upload a statement file (`.md`, `.txt`, `.docx`, `.pdf`) for a problem.
 * Sends the file as multipart/form-data.
 *
 * POST /api/v1/problems/{id}/statement
 */
export async function uploadStatement(
  problemId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);

  // Do NOT set Content-Type manually — the browser sets it with the boundary.
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return request<void>(`/api/v1/problems/${problemId}/statement`, {
    method: "POST",
    headers,
    body: formData,
    authenticated: false, // header already set above
  });
}

/**
 * Upload a testcase ZIP archive for a problem.
 * Sends the file as multipart/form-data.
 *
 * POST /api/v1/problems/{id}/testcases
 */
export async function uploadTestcases(
  problemId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);

  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return request<void>(`/api/v1/problems/${problemId}/testcases`, {
    method: "POST",
    headers,
    body: formData,
    authenticated: false, // header already set above
  });
}

// ---------------------------------------------------------------------------
// Submissions
// ---------------------------------------------------------------------------

/**
 * Submit source code for judging.
 *
 * POST /api/v1/submissions/
 */
export async function submitCode(data: SubmissionCreate): Promise<Submission> {
  return request<Submission>("/api/v1/submissions/", {
    method: "POST",
    headers: buildHeaders(true),
    body: JSON.stringify(data),
  });
}

/**
 * Fetch the current user's submission history (paginated, 25 per page).
 *
 * GET /api/v1/submissions/?page={page}
 */
export async function getSubmissions(page = 1): Promise<Submission[]> {
  return request<Submission[]>(`/api/v1/submissions/?page=${page}`, {
    method: "GET",
    headers: buildHeaders(true),
  });
}

/**
 * Fetch a single submission by its ID.
 *
 * GET /api/v1/submissions/{id}
 */
export async function getSubmission(id: string): Promise<Submission> {
  return request<Submission>(`/api/v1/submissions/${id}`, {
    method: "GET",
    headers: buildHeaders(true),
  });
}

// ---------------------------------------------------------------------------
// Convenience namespace export (optional — callers can also import named)
// ---------------------------------------------------------------------------

const apiClient = {
  login,
  logout,
  requestPasswordReset,
  confirmPasswordReset,
  getProblems,
  getProblem,
  createProblem,
  uploadStatement,
  uploadTestcases,
  submitCode,
  getSubmissions,
  getSubmission,
};

export default apiClient;
