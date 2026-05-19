"use client";

export default function StudentDashboard() {
  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Student Dashboard</h1>
        <button 
          onClick={() => fetch("/api/auth/logout", { method: "POST" }).then(() => window.location.href = "/login")}
          className="btn btn-secondary"
        >
          Đăng xuất
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Bài tập chưa làm</h3>
          <p className="text-4xl font-bold text-primary-600">5</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Xếp hạng</h3>
          <p className="text-4xl font-bold text-primary-600">#12</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Tỷ lệ Accepted</h3>
          <p className="text-4xl font-bold text-primary-600">85%</p>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-2xl mb-4">Hoạt động gần đây</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold">Sum Two Numbers</p>
              <p className="text-sm text-gray-500">2 giờ trước</p>
            </div>
            <span className="verdict-badge verdict-ac">Accepted</span>
          </div>
        </div>
      </div>
    </div>
  );
}
