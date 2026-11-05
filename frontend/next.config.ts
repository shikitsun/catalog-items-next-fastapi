import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: false,
  partialPrefetching: false,
  output: "standalone",
  trailingSlash: true,
  allowedDevOrigins: [
    "localhost:8080",
    "127.0.0.1:8080",
    "localhost:3000",
    "127.0.0.1:3000",
  ],
  images: {
    unoptimized: true,
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
