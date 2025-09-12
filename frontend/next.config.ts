import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',                 // any request starting with /api/
        destination: 'http://127.0.0.1:8000/:path*', // proxies to FastAPI
      },
    ]
  },
};

export default nextConfig;
