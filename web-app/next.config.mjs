/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produces a standalone build output for Docker deployment.
  output: "standalone",

  // Enable React Strict Mode
  reactStrictMode: true,

  // Forward API requests to the FastAPI backend during development.
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
