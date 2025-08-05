import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "./components/common/Header";
import { ClerkProvider, SignedIn} from "@clerk/nextjs";
import Footer from "./components/common/Footer";
import Navigation from "./components/common/Navigation";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hanten App",
  description: "Reverse debate app",
};



export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="ja">
        <body className={`${geistSans.variable} ${geistMono.variable} container`}>

          <Header />
          <SignedIn>
            <Navigation/>
          </SignedIn>
          <main className="main-content">
            {children}
          </main>
          <Footer />

        </body>
      </html>
    </ClerkProvider>
  );
}
