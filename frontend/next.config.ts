// frontend/next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
    async rewrites() {
        return [
            {
                // Source: All frontend requests to /api/
                source: '/api/:path*', 
                // Destination: Forwarded to your Python FastAPI server
                destination: 'http://127.0.0.1:5000/api/:path*', 
            },
        ];
    },
};

export default nextConfig;