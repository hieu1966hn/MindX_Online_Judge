"use client";

export default function AdminDashboard() {
  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <button 
          onClick={() => fetch("/api/auth/logout", { method: "POST" }).then(() => window.location.href = "/login")}
          className="btn btn-secondary"
        >
          Đăng xuất
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Users</h3>
          <p className="text-4xl font-bold text-primary-600">128</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Problems</h3>
          <p className="text-4xl font-bold text-primary-600">24</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">Submissions</h3>
          <p className="text-4xl font-bold text-primary-600">1.2k</p>
        </div>
        <div className="card card-hover">
          <h3 className="text-xl mb-2">System</h3>
          <p className="text-4xl font-bold text-green-600">OK</p>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-2xl mb-4">Quản trị hệ thống</h2>
        <p className="text-gray-600">Round 3 sẽ triển khai quản lý users, problems và submissions tại đây.</p>
      </div>
    </div>
  );
}
