"use client";

import { useEffect, useState } from "react";
import { getProblems } from "@/lib/api";
import type { Problem } from "@/types";
import Link from "next/link";

/**
 * Student Problem List Page
 * 
 * Displays all visible problems with:
 * - Problem code, title, time/memory limits
 * - Difficulty indicator (via color coding)
 * - Link to problem detail page
 */
export default function StudentProblemsPage() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProblems() {
      try {
        const data = await getProblems();
        setProblems(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load problems");
      } finally {
        setLoading(false);
      }
    }
    fetchProblems();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="card bg-red-50 border-red-200">
          <h2 className="text-xl font-bold text-red-700 mb-2">Lỗi tải dữ liệu</h2>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Danh sách bài tập</h1>
          <p className="text-gray-600 mt-1">
            Chọn bài tập để xem đề và nộp code
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Tổng: <span className="font-semibold text-gray-900">{problems.length}</span> bài
        </div>
      </div>

      {problems.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 text-lg">Chưa có bài tập nào</p>
        </div>
      ) : (
        <div className="space-y-3">
          {problems.map((problem) => (
            <Link
              key={problem.id}
              href={`/student/problems/${problem.id}`}
              className="card card-hover block group"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono text-sm font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded">
                      {problem.code}
                    </span>
                    <h3 className="text-xl font-bold group-hover:text-primary-600 transition-colors">
                      {problem.title}
                    </h3>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {problem.time_limit_ms}ms
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                      </svg>
                      {problem.memory_limit_mb}MB
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                      {problem.allowed_languages.join(", ")}
                    </span>
                  </div>
                </div>
                <svg 
                  className="w-6 h-6 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
