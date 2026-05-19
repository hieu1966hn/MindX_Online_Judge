"use client";

import { useEffect, useState } from "react";
import { getSubmission } from "@/lib/api";
import type { Submission } from "@/types";
import VerdictBadge from "@/components/submission/VerdictBadge";
import Link from "next/link";

/**
 * Submission Detail Page
 * 
 * Shows:
 * - Final verdict and score
 * - Per-testcase results table
 * - Compile error details if any
 * - Submission metadata (time, language)
 */
export default function SubmissionDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSubmission() {
      try {
        const data = await getSubmission(id);
        setSubmission(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load submission");
      } finally {
        setLoading(false);
      }
    }
    fetchSubmission();
  }, [id]);

  if (loading) return <div className="p-8">Loading...</div>;
  if (error || !submission) return <div className="p-8 text-red-600">{error || "Not found"}</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Chi tiết Submission</h1>
        <Link href={`/student/problems/${submission.problem_id}`} className="btn btn-secondary btn-sm">
          Quay lại bài tập
        </Link>
      </div>

      <div className="card grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-1">
          <p className="text-xs text-gray-500 uppercase font-bold">Trạng thái</p>
          <VerdictBadge verdict={submission.verdict} className="text-lg" />
        </div>
        <div className="space-y-1">
          <p className="text-xs text-gray-500 uppercase font-bold">Điểm số</p>
          <p className="text-2xl font-bold text-primary-600">{submission.score ?? 0}/100</p>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-gray-500 uppercase font-bold">Thời gian nộp</p>
          <p className="text-sm">{new Date(submission.created_at).toLocaleString()}</p>
        </div>
      </div>

      {submission.compile_error && (
        <div className="card border-red-200 bg-red-50">
          <h3 className="text-lg font-bold text-red-700 mb-2">Compile Error</h3>
          <pre className="font-mono text-sm text-red-600 overflow-x-auto p-4 bg-white rounded border border-red-100">
            {submission.compile_error}
          </pre>
        </div>
      )}

      <div className="card overflow-hidden p-0">
        <div className="p-4 border-b bg-gray-50 font-bold">Kết quả từng Testcase</div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-xs uppercase text-gray-500 border-b">
                <th className="px-6 py-3">#</th>
                <th className="px-6 py-3">Kết quả</th>
                <th className="px-6 py-3">Thời gian</th>
                <th className="px-6 py-3">Loại</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {submission.testcase_results.map((res, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-mono">{res.index}</td>
                  <td className="px-6 py-4">
                    <VerdictBadge verdict={res.verdict} />
                  </td>
                  <td className="px-6 py-4 font-mono text-sm">{res.runtime_ms}ms</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${res.is_hidden ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>
                      {res.is_hidden ? 'Hidden' : 'Sample'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
