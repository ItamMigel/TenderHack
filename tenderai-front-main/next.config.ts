import type { NextConfig } from "next";


const nextConfig: NextConfig = {

    /* config options here */
    reactStrictMode: false,
    eslint: { ignoreDuringBuilds: true, },
    typescript: { ignoreBuildErrors: true },
    crossOrigin: "anonymous",

    async headers () {
        console.log("Huh?");
        return [
            {
                // matching all API routes
                source: "/api/:path*",
                headers: [
                    {
                        key: "Access-Control-Allow-Credentials",
                        value: "true"
                    },
                    {
                        key: "Access-Control-Allow-Origin",
                        value: "*"
                    }, // replace this your actual origin
                    {
                        key: "Access-Control-Allow-Methods",
                        value: "GET,DELETE,PATCH,POST,PUT"
                    },
                    {
                        key: "Access-Control-Allow-Headers",
                        value: "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version"
                    },
                ]
            }
        ];
    },
    webpack (config) {
        config.module.rules.push({
            test: /\.svg$/,
            use: ["@svgr/webpack"],
        });
        return config;
    },

};

export default nextConfig;
