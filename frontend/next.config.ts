import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*', 
                destination: 'http://127.0.0.1:8000/api/:path*', 
            },
        ];
    },
    
    // Optional: Add TypeScript path aliases
    typescript: {
        // Optionally add path aliases
        tsconfigPath: './tsconfig.json'
    }
};

export default nextConfig;