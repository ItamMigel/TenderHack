import * as React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../globals.css";
import { HeroUIProvider } from "@heroui/react";


const inter = Inter({
    variable: "--font-inter",
    subsets: ["latin", "cyrillic"],
});

export const metadata: Metadata = {
    title: "Create Next App",
    description: "Generated by create next app",
};

export default function RootLayout ({ children, }: Readonly<{children: React.ReactNode;}>) {
    return (
        <html>
            <body
                className = {`${inter.variable} bg-white text-text-black`}
            >
                <HeroUIProvider>
                    <div className = "h-scree flex">
                        <div className = "mx-auto">
                            {children}

                        </div>
                    </div>
                </HeroUIProvider>
            </body>
        </html>
    );
}
