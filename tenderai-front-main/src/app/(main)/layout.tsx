import Sidebar from "@/components/sidebar";
import React, { useEffect } from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/app/globals.css";
import { HeroUIProvider } from "@heroui/react";
import { MainContextProvider } from "@/components/context";


const inter = Inter({
    variable: "--font-inter",
    subsets: ["latin", "cyrillic"],
});

export const metadata: Metadata = {
    title: "14-Bit MISIS AI",
    description: "14-Bit MISIS AI",
};

export default function RootLayout ({ children, }: Readonly<{children: React.ReactNode;}>) {
    return (
        <html>
            <body
                className = {`${inter.variable} overflow-hidden bg-white`}
            >
                <MainContextProvider>
                    <HeroUIProvider>
                        <div className = "flex items-start gap-x-4 text-text-black">
                            <div className = "h-screen shrink-0">
                                <Sidebar/>

                            </div>
                            <div className = "h-screen min-w-0 flex-1 pr-4">
                                <div className = "mx-auto h-full">
                                    {children}

                                </div>

                            </div>
                        </div>
                    </HeroUIProvider>
                </MainContextProvider>
            </body>
        </html>
    );
}
