"use client";

export default function TeacherDashboard() {
  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Teacher Dashboard</h1>
        <button 
          onClick={() => fetch("/api/auth/logout", { method: "POST" }).then(() => window.location.href = "/login")}
          className="btn btn-secondary"
        >
          Đăng xuất
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Bài tập đã tạo</h3>
          <p className="text-4xl font-bold text-primary-600">12</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Submissions hôm nay</h3>
          <p className="text-4xl font-bold text-primary-600">48</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Học viên active</h3>
          <p className="text-4xl font-bold text-primary-600">32</p>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-2xl mb-4">Quản lý bài tập</h2>
        <p className="text-gray-600">Round 3 sẽ triển khai Problem Management UI tại đây.</p>
      </div>
    </div>
  );
}
