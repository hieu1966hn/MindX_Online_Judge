"use client";

import { useEffect, useState } from "react";
import { getProblem, getSubmission, submitCode } from "@/lib/api";
import type { Problem, Submission } from "@/types";
import CodeEditor from "@/components/editor/CodeEditor";
import VerdictBadge from "@/components/submission/VerdictBadge";
import Link from "next/link";

/**
 * Student Problem Detail Page
 * 
 * Features:
 * - Problem statement (Markdown)
 * - Constraints (Time, Memory)
 * - Code Editor (Monaco)
 * - Real-time submission flow with polling
 */
export default function ProblemDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Editor state
  const [sourceCode, setSourceCode] = useState("");
  const [language, setLanguage] = useState<"python" | "cpp">("python");
  const [submitting, setSubmitting] = useState(false);
  const [lastSubmission, setLastSubmission] = useState<Submission | null>(null);

  useEffect(() => {
    async function fetchProblem() {
      try {
        const data = await getProblem(id);
        setProblem(data);
        // Default code
        if (language === "python") {
           setSourceCode("# Nhập code Python của bạn\n\n");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load problem");
      } finally {
        setLoading(false);
      }
    }
    fetchProblem();
  }, [id, language]);

  const handleSubmit = async () => {
    if (!sourceCode.trim()) return;
    
    setSubmitting(true);
    setLastSubmission(null);
    try {
      const submission = await submitCode({
        problem_id: id,
        language: language === "python" ? "python3" : "cpp",
        source_code: sourceCode,
      });
      setLastSubmission(submission);
      
      // Poll for result if pending
      if (submission.verdict === "PD") {
        pollSubmission(submission.id);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  const pollSubmission = async (subId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/submissions/${subId}`, {
          headers: {
            'Authorization': `Bearer ${document.cookie.split('access_token=')[1]?.split(';')[0]}`
          }
        });
        if (response.ok) {
          const data: Submission = await response.json();
          setLastSubmission(data);
          if (data.verdict !== "PD") {
            clearInterval(interval);
          }
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 2000);
  };

  if (loading) return <div className="p-8 animate-pulse">Loading...</div>;
  if (error || !problem) return <div className="p-8 text-red-600">{error || "Problem not found"}</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 h-[calc(100vh-64px)] overflow-hidden">
      {/* Left: Problem Statement */}
      <div className="flex flex-col border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 overflow-y-auto scrollbar-thin">
        <div className="p-6 space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold mb-2">{problem.title}</h1>
              <div className="flex gap-2">
                <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">{problem.code}</span>
                <span className="text-xs font-semibold text-primary-600">MEDIUM</span>
              </div>
            </div>
            <Link 
              href={`/student/problems/${id}/submissions`}
              className="text-sm text-primary-600 hover:underline"
            >
              Lịch sử nộp bài
            </Link>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
              <p className="text-xs text-gray-500 uppercase font-bold">Giới hạn thời gian</p>
              <p className="text-lg font-mono">{problem.time_limit_ms} ms</p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
              <p className="text-xs text-gray-500 uppercase font-bold">Giới hạn bộ nhớ</p>
              <p className="text-lg font-mono">{problem.memory_limit_mb} MB</p>
            </div>
          </div>

          <div className="prose dark:prose-invert max-w-none">
            <h3 className="text-lg font-bold">Đề bài</h3>
            <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
              {problem.statement_md || "Không có nội dung đề bài."}
            </div>
          </div>
        </div>
      </div>

      {/* Right: Editor & Results */}
      <div className="flex flex-col bg-gray-50 dark:bg-gray-800 overflow-hidden">
        <div className="flex-1 p-4 overflow-y-auto scrollbar-thin">
          <CodeEditor
            value={sourceCode}
            onChange={setSourceCode}
            language={language}
            onLanguageChange={setLanguage}
          />
          
          {/* Status Bar / Results */}
          <div className="mt-4 space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                {lastSubmission && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">Kết quả cuối:</span>
                    <VerdictBadge verdict={lastSubmission.verdict} />
                    {lastSubmission.score !== null && (
                      <span className="font-bold text-primary-600">Score: {lastSubmission.score}</span>
                    )}
                  </div>
                )}
              </div>
              <button
                onClick={handleSubmit}
                disabled={submitting || !sourceCode.trim()}
                className={`btn btn-primary px-8 ${submitting ? 'opacity-70 cursor-wait' : ''}`}
              >
                {submitting ? 'Đang gửi...' : 'Nộp bài'}
              </button>
            </div>

            {lastSubmission?.compile_error && (
              <div className="card bg-red-50 border-red-200 p-4">
                <p className="text-xs font-bold text-red-700 uppercase mb-2">Compile Error</p>
                <pre className="text-xs font-mono text-red-600 whitespace-pre-wrap">
                  {lastSubmission.compile_error}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
