/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@million-pocket/database', '@million-pocket/api-client'],
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
};

module.exports = nextConfig;
