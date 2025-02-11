import { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*", // Matches /api/hello
        destination: "http://127.0.0.1:5000/api/:path*", // Proxy to Flask backend
      },
    ];
  },
};

export default nextConfig;
