import "./globals.css"

export const metadata = {
  title: "MindX Online Judge",
  description: "Hệ thống chấm bài lập trình nội bộ cho học viên và giảng viên MindX",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  )
}
