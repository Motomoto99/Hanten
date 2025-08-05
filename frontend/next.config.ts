import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // 警告: これを設定すると、ESLintのエラーがあっても
    // 本番用のビルドが成功するようになります。
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
