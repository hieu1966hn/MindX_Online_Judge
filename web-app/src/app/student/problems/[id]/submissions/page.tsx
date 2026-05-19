"use client";

import { useEffect, useState } from "react";
import { getSubmissions } from "@/lib/api";
import type { Submission } from "@/types";
import VerdictBadge from "@/components/submission/VerdictBadge";
import Link from "next/link";

/**
 * Student Problem Submissions Page
 * 
 * Lists all submissions by the current student for a specific problem.
 */
export default function ProblemSubmissionsPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSubmissions() {
      try {
        // Current API getSubmissions() gets ALL submissions of user.
        // In a real app we might filter by problem_id on server.
        // For MVP, we'll fetch all and filter here or just show recent.
        const data = await getSubmissions();
        setSubmissions(data.filter(s => s.problem_id === id));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load submissions");
      } finally {
        setLoading(false);
      }
    }
    fetchSubmissions();
  }, [id]);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Lịch sử nộp bài</h1>
          <p className="text-gray-500">Xem lại các lần giải bài của bạn</p>
        </div>
        <Link href={`/student/problems/${id}`} className="btn btn-secondary">
          Quay lại bài tập
        </Link>
      </div>

      {submissions.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">Bạn chưa nộp bài này lần nào.</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-50 border-b text-xs uppercase text-gray-500 font-bold">
                <th className="px-6 py-4">Thời gian</th>
                <th className="px-6 py-4">Kết quả</th>
                <th className="px-6 py-4">Điểm</th>
                <th className="px-6 py-4">Ngôn ngữ</th>
                <th className="px-6 py-4 text-right">Chi tiết</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {submissions.map((sub) => (
                <tr key={sub.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(sub.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <VerdictBadge verdict={sub.verdict} />
                  </td>
                  <td className="px-6 py-4 font-bold text-primary-600">
                    {sub.score ?? 0}
                  </td>
                  <td className="px-6 py-4 font-mono text-sm uppercase">
                    {sub.language}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link 
                      href={`/student/submissions/${sub.id}`}
                      className="text-primary-600 hover:text-primary-700 font-semibold text-sm"
                    >
                      Xem code →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
