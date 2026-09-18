import type { NextConfig } from "next";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://leadhunter-ai-production.up.railway.app";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_BASE}/api/:path*`,
      },
      {
        source: "/demo/:path*",
        destination: `${API_BASE}/demo/:path*`,
      },
      {
        source: "/preview/:path*",
        destination: `${API_BASE}/preview/:path*`,
      },
    ];
  },
};

export default nextConfig;