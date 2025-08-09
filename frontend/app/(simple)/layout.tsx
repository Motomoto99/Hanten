'use client'

import { SignedIn } from "@clerk/nextjs";
import Header from "../components/common/Header";
import Navigation from "../components/common/Navigation";
import Footer from "../components/common/Footer";
import Link from "next/link";

export default function RootAuthLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <>
            <header className='header'>
                <Link href="/" className='hanten-logo'>
                    Hanten
                </Link>
                {/* 右側のボタンをまとめるdiv */}
                <div className="header-actions">
                </div>
            </header>
            <main className="main-content">
                {children}
            </main>
            <Footer />
        </>
    );
}