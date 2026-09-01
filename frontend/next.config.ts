import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits .next/standalone for the production VPS Docker image
  // (docs/deployment/DEPLOYMENT_SPEC.md); does not affect `next dev`.
  output: "standalone",
};

export default nextConfig;
