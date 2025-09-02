'use client'

import { SignedIn } from "@clerk/nextjs";
import Header from "../components/common/Header";
import Navigation from "../components/common/Navigation";
import Footer from "../components/common/Footer";

export default function RootAuthLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <>
            <main className="simple-main-content">
                {children}
            </main>
        </>
    );
}