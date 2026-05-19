"use client";

import { Editor } from "@monaco-editor/react";
import { useState, useRef } from "react";

/**
 * CodeEditor Component
 * 
 * Monaco Editor wrapper with:
 * - Language switching (Python, C++)
 * - File upload support (.py, .cpp)
 * - 64KB file size limit
 * - Dark/light theme support
 */

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: "python" | "cpp";
  onLanguageChange: (lang: "python" | "cpp") => void;
  readOnly?: boolean;
}

const LANGUAGE_CONFIG = {
  python: {
    label: "Python 3",
    monacoLang: "python",
    extensions: [".py"],
    defaultCode: "# Nhập code Python của bạn\n\n",
  },
  cpp: {
    label: "C++",
    monacoLang: "cpp",
    extensions: [".cpp", ".cc", ".cxx"],
    defaultCode: "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Nhập code C++ của bạn\n    \n    return 0;\n}\n",
  },
};

const MAX_FILE_SIZE = 64 * 1024; // 64KB

export default function CodeEditor({
  value,
  onChange,
  language,
  onLanguageChange,
  readOnly = false,
}: CodeEditorProps) {
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadError(null);

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      setUploadError(`File quá lớn (${(file.size / 1024).toFixed(1)}KB). Giới hạn: 64KB`);
      return;
    }

    // Check extension
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    const config = LANGUAGE_CONFIG[language];
    if (!config.extensions.includes(ext)) {
      setUploadError(`File extension không hợp lệ. Chỉ chấp nhận: ${config.extensions.join(", ")}`);
      return;
    }

    // Read file
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      onChange(content);
    };
    reader.onerror = () => {
      setUploadError("Không thể đọc file");
    };
    reader.readAsText(file);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center gap-2">
          <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Ngôn ngữ:
          </label>
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as "python" | "cpp")}
            disabled={readOnly}
            className="px-3 py-1.5 border rounded-md bg-white dark:bg-gray-700 text-sm font-medium focus:ring-2 focus:ring-primary-500 outline-none disabled:opacity-50"
          >
            <option value="python">{LANGUAGE_CONFIG.python.label}</option>
            <option value="cpp">{LANGUAGE_CONFIG.cpp.label}</option>
          </select>
        </div>

        {!readOnly && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-secondary text-sm py-1.5 px-3"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload File
          </button>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept={LANGUAGE_CONFIG[language].extensions.join(",")}
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Upload Error */}
      {uploadError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {uploadError}
        </div>
      )}

      {/* Monaco Editor */}
      <div className="border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden">
        <Editor
          height="500px"
          language={LANGUAGE_CONFIG[language].monacoLang}
          value={value}
          onChange={(val) => onChange(val || "")}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: "on",
            rulers: [80],
            wordWrap: "on",
            readOnly,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: language === "python" ? 4 : 2,
            insertSpaces: true,
          }}
        />
      </div>

      <p className="text-xs text-gray-500">
        💡 Tip: Bạn có thể upload file code hoặc gõ trực tiếp vào editor. Giới hạn: 64KB.
      </p>
    </div>
  );
}
