import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
  images: {
    formats: ["image/avif", "image/webp"],
  },
  compress: true,
};

export default nextConfig;
