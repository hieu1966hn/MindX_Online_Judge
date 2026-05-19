/**
 * TypeScript type definitions for submissions.
 *
 * Mirrors the backend schemas in api-server/app/schemas/submission.py
 * and the Submission model in api-server/app/models/submission.py.
 */

/** Possible verdict values for a submission or individual testcase. */
export type Verdict = "PD" | "AC" | "WA" | "TLE" | "RE" | "CE";

/** Result for a single testcase within a submission. */
export interface TestcaseResult {
  index: number;
  verdict: Verdict;
  runtime_ms: number;
  /** Hidden testcases do not expose expected/actual output to students. */
  is_hidden: boolean;
}

/** A submission as returned by the API. */
export interface Submission {
  id: string;
  problem_id: string;
  user_id: string;
  language: string;
  source_path: string;
  verdict: Verdict;
  score: number | null;
  compile_error: string | null;
  testcase_results: TestcaseResult[];
  judged_at: string | null;
  /** ISO 8601 datetime string */
  created_at: string;
}

/** Payload for submitting code. */
export interface SubmissionCreate {
  problem_id: string;
  language: string;
  source_code: string;
}
